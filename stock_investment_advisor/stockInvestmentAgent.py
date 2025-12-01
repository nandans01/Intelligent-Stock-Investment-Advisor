# main_stock_agent.py
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent, LlmAgent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.runners import InMemoryRunner
from google.adk.plugins.logging_plugin import (
    LoggingPlugin,
)  # <---- 1. Import the Plugin
from google.adk.tools import AgentTool, FunctionTool, google_search
from google.genai import types
from google.adk.models.google_llm import Gemini

from google.adk.tools.agent_tool import AgentTool
import yfinance as yf
import pandas as pd
import json
from datetime import datetime
import asyncio

# --- Step 1 & 2: Define Tools and Agents ---


retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)

# Ticker Extraction Agent
ticker_agent = Agent(
    name="ticker_agent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
        ),
    description="Identifies one or more stock ticker symbols from a user's query. Returns a single ticker or a comma-separated list.",
    instruction="""
    You are an expert financial market analyst specializing in identifying stock ticker symbols.

    Your task is to find all company names mentioned in a user's query and return their corresponding stock ticker symbols.

    ### RULES
    - If one company is found, return its single stock ticker symbol in uppercase (e.g., "AAPL").
    - If multiple companies are found, return their ticker symbols as a single, comma-separated string (e.g., "AAPL,GOOGL,MSFT").
    - If a company has multiple tickers, return the most common one.
    - If no ticker can be identified for any company, return the string "UNKNOWN".
    - Your output MUST BE ONLY the ticker symbol(s). Do not include any explanations, labels, or other text.

    ### EXAMPLES
    - Query: "Tell me about Apple" -> "AAPL"
    - Query: "Should I invest in Microsoft and Google?" -> "MSFT,GOOGL"
    - Query: "What's the news on Abbott Laboratories?" -> "ABT"
    - Query: "What about that car company?" -> "UNKNOWN"
    """,
    output_key="ticker_symbol"
)

# Stock Price Retrieval Tool
def get_stock_price(ticker: str) -> dict:
    """
    Get 1 year stock price data for a given ticker.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')

    Returns:
        dict: Dictionary containing stock price data

        On Success:
            {
                'ticker': str - Stock ticker symbol
                'current_price': float - Latest closing price
                'start_date': str - Start date of data (YYYY-MM-DD)
                'end_date': str - End date of data (YYYY-MM-DD)
                'high_52w': float - 52-week high price
                'low_52w': float - 52-week low price
                'avg_volume': float - Average trading volume
            }

        On Error:
            {
                'ticker': str - Stock ticker symbol
                'error': str - Error message describing what went wrong
                'data': None
            }
    """
    try:
        print(f"Fetching data for ticker: {ticker}")
        stock = yf.Ticker(ticker)
        data = stock.history(period="1y")

        if data.empty:
            return {
                "ticker": ticker,
                "error": f"No data found for ticker: {ticker}",
                'data': None}

        current_price = data['Close'].iloc[-1]
        high_52w = data['High'].max()
        low_52w = data['Low'].min()
        avg_volume = data['Volume'].mean()
        print(f"Current Price: {current_price}, 52-Week High: {high_52w}, 52-Week Low: {low_52w}, Average Volume: {avg_volume}")

        # Format DataFrame for readability
        #data_formatted = data.reset_index().to_json(orient='records', date_format='iso')

        result = {
            "ticker": ticker,
            "current_price": current_price,
            "start_date": data.index.min().strftime('%Y-%m-%d'),
            "end_date": data.index.max().strftime('%Y-%m-%d'),
            "high_52w": high_52w,
            "low_52w": low_52w,
            "avg_volume": avg_volume
        }
        print(f"Returning Ticker: {result['ticker']} data successfully.")
        return result
    except Exception as e:
        print(f"Error fetching data for ticker: {ticker}. Error: {str(e)}")
        return {
            "ticker": ticker,
            "error": str(e),
            "data": None
            }

# News Retrieval Agent
news_agent = Agent(
    name="news_agent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    description="Accepts ticker symbol(s) and provides news summaries for each stock.",
    instruction="""
    You are a financial news analyst. You will receive either a single ticker (e.g., "AAPL") or a comma-separated list of tickers (e.g., "AAPL,GOOGL").

    For EACH ticker:
    1. Use the `google_search` tool to find 2-3 most relevant recent news articles
    2. Summarize the key news that could impact that stock's value

    Format your output as a JSON object where keys are ticker symbols and values are news summaries:
    {"AAPL": "summary text", "GOOGL": "summary text"}
    """,
    tools=[google_search],
    output_key="stock_news"
)


# Stock Data Retrieval Agent
stock_data_agent = Agent(
    name="stock_data_agent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    tools=[get_stock_price],
    description="Fetches historical stock data for given ticker symbols using get_stock_price tool.",
    instruction="""
    You are a STOCK PRICE DATA FETCHER. Your ONLY job is to call the get_stock_price tool for each ticker symbol provided.

    ### MANDATORY BEHAVIOR
    When you receive ticker symbols (like "GOOGL,TSLA"), you MUST:
    1. IMMEDIATELY call get_stock_price("GOOGL")
    2. IMMEDIATELY call get_stock_price("TSLA")
    3. Return the data in JSON format

    ### WHAT YOU MUST NOT DO
    - NEVER say "I cannot provide investment advice"
    - NEVER ask "Would you like me to fetch data"
    - NEVER mention investment advice or recommendations
    - NEVER hesitate or ask for permission
    - NEVER explain what you're about to do

    ### YOUR EXACT BEHAVIOR
    Input: "GOOGL,TSLA"
    Your action: Call get_stock_price for each ticker immediately
    Your output: JSON with the data

    ### EXAMPLE WORKFLOW
    Receive: "AAPL,GOOGL"
    Action 1: get_stock_price("AAPL")
    Action 2: get_stock_price("GOOGL")
    Output: {"AAPL": {...data...}, "GOOGL": {...data...}}

    ### NO CONVERSATION - ONLY DATA
    You are NOT a conversational agent. You are a data fetching function.
    Process the tickers and return the data. That's it.

    ### RESPONSE RULES
    - Start calling get_stock_price immediately upon receiving tickers
    - Return JSON mapping ticker symbols to their price data
    - Include any errors exactly as returned by get_stock_price
    - No explanatory text, no questions, no conversation
    """,
    output_key="stock_price_data"
)

# Parallel agent to fetch news and price data concurrently for all tickers
parallel_data_agent = ParallelAgent(
    name="parallel_data_agent",
    sub_agents=[news_agent, stock_data_agent],
    description="Fetches news and stock price data concurrently for all tickers."
)


# Recommendation Aggregator Agent
stock_recommendation_agent = Agent(
    name="stock_recommendation_agent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    description=(
        "Analyzes a list of stock data and news summaries to generate a structured JSON equity recommendation."
    ),
    instruction=r"""
    You are an expert equity recommendation agent. Your role is to synthesize data from previous steps and provide an informational investment suggestion in a structured JSON format. This is NOT financial advice.

    ### CONTEXT
    You will receive a dictionary with:
    - `ticker_symbol`: comma-separated list of tickers (e.g., "AAPL,GOOGL")
    - `parallel_data_agent`: A dictionary containing outputs from parallel execution:
        - `stock_news`: JSON object with ticker keys and news summaries as values
        - `stock_price_data`: JSON object with ticker keys and price data as values

    ### TASK
    Generate a recommendation for EACH stock in the ticker list with a ONE-YEAR price target.

    ### STEPS
    1.  **Parse the Input**:
        - Extract all tickers from `ticker_symbol` (split by comma if needed)
        - Access `stock_news` from `parallel_data_agent['stock_news']`
        - Access `stock_price_data` from `parallel_data_agent['stock_price_data']`
        - **IMPORTANT**: `stock_price_data` may be structured in two ways:
            a) Nested: `{"AAPL": {"ticker": "AAPL", "current_price": 150.25, ...}, "GOOGL": {...}}`
            b) Direct: `{"ticker": "AAPL", "current_price": 150.25, ...}` (single stock)
        - Handle both cases: If `stock_price_data` contains a 'ticker' key at the root level, it's a single stock (case b). Otherwise, it's nested (case a).

    2.  **Analyze Each Stock**:
        - **Historical Performance**: Review the 52-week high/low range, current price position, and average volume
        - **Recent Momentum**: Determine if the stock is trending up, down, or consolidating
        - **News Sentiment**: Identify positive catalysts (growth, innovation, earnings beats, partnerships) or negative factors (regulations, competition, earnings misses, management changes)
        - **Risk Assessment**: Consider market conditions, sector trends, and company-specific risks

    3.  **Calculate One-Year Target Price**:
        - Base your target on a combination of:
            * **Technical Analysis**: Current price relative to 52-week range (is it near lows = potential upside, or near highs = limited room)
            * **Fundamental Catalysts**: News-driven factors (product launches, earnings growth, market expansion)
            * **Realistic Growth**: Apply a reasonable annual growth rate (5-30% depending on company maturity and sector)
            * **Risk Adjustment**: Reduce target if negative news or downtrend; increase if strong positive momentum
        - Example calculations:
            * Strong Buy: Current price × 1.20 to 1.30 (20-30% upside)
            * Buy: Current price × 1.05 to 1.20 (5-20% upside)
            * Hold: Current price × 0.95 to 1.05 (-5% to +5%)
            * Sell: Current price × 0.80 to 0.95 (down 5-20%)

    4.  **Formulate Recommendation**: For each stock, create a JSON object with:
        -   `ticker`: The stock ticker symbol
        -   `recommendation`: One of **"Buy"**, **"Hold"**, or **"Sell"**
        -   `current_price`: The current stock price (float)
        -   `target_price`: Your calculated one-year target price (float) based on the analysis above
        -   `rationale`: A 2-3 sentence justification that MUST explain:
            * The key factors (price momentum + news sentiment) driving your target
            * The expected percentage gain/loss
            * Why the target is achievable in one year

    ### RULES
    -   **CRITICAL**: Your output MUST be only a list of JSON objects. No other text, explanations, or markdown.
    -   The `target_price` must be a data-driven estimate based on current price, historical range, and news sentiment - not arbitrary.
    -   If price data for a stock contains an 'error' key, reflect this in its `rationale` and do not provide a recommendation or target price.
    -   If news is empty or unhelpful, base your target primarily on technical analysis and mention the limitation.
    -   Keep the `rationale` short, clear, and neutral. This is an informational summary, not financial advice.
    """,
    output_key="recommendation_result"
)

#4. Define the top-level agent that runs the entire workflow
stock_analysis_agent = SequentialAgent(
    name="stock_analysis_agent",
    sub_agents=[ticker_agent, parallel_data_agent, stock_recommendation_agent],
)

# Bank Agent - Remote A2A Agent for Bank Balance
bank_agent = RemoteA2aAgent(
    name="bank_balance_agent",
    description="Agent that returns the bank balance.",
    agent_card=(
        f"http://localhost:8001/a2a/bank_balance_agent{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)

# Portfolio Allocation Agent
portfolio_allocation_agent = Agent(
    name="portfolio_allocation_agent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    tools=[AgentTool(bank_agent)],
    description="Allocates available cash among stocks with Buy recommendations.",
    instruction="""
    You are a portfolio allocation specialist. Your role is to allocate available cash among stocks with "Buy" recommendations from the previous stock analysis. You do NOT fetch any external data or execute actual stock purchases.

    ### DATA SOURCES (STRICTLY LIMITED)
    1. `recommendation_result` from stock_analysis_agent (provided in your context)
    2. `bank_agent` - Remote A2A agent (only for cash balance)

    ### AVAILABLE TOOLS (ONLY ONE)
    - `bank_agent`: Remote A2A agent that returns available cash balance information

    ### ABSOLUTELY FORBIDDEN ACTIONS
    - Do NOT call google_search, get_stock_price, or any data retrieval tools
    - Do NOT access external APIs, websites, or internet resources
    - Do NOT call buy_stocks, purchase_stocks, execute_trades, or any trading tools
    - Do NOT fetch current market prices (use prices from recommendation_result)
    - Do NOT look up additional company information

    ### INPUT CONTEXT STRUCTURE
    You will receive context containing:
    - `recommendation_result`: Array of stock recommendations from stock_analysis_agent with:
        * ticker: Stock symbol (e.g., "GOOGL", "TSLA")
        * recommendation: "Buy", "Hold", or "Sell"
        * current_price: Stock price as float (from previous analysis)
        * target_price: One-year target price as float
        * rationale: Analysis explanation

    ### TASK: ALLOCATION CALCULATION ONLY
    1. **Display Input Data**: First, display the recommendation_result received from stock_analysis_agent to show what data you're working with
    2. **Get Available Cash ONCE**: Call `bank_agent` ONE TIME ONLY to determine available funds
    3. **Extract Stock Data**: Use ONLY the recommendation_result from context
    4. **Filter Buy Recommendations**: Identify stocks where recommendation == "Buy"
    5. **Equal Cash Allocation**: Divide available cash equally among Buy stocks
    6. **Calculate Share Quantities**: Use current_price from recommendation_result
    7. **Return Allocation Plan**: JSON format with calculations

    ### STEP-BY-STEP PROCESS (CALL bank_agent ONLY ONCE)
    Step 1: Display received recommendation_result data
    Step 2: Call bank_agent ONE TIME to get available cash
    Step 3: Filter for Buy recommendations only
    Step 4: Calculate allocation and share quantities using the cash amount from Step 2
    Step 5: Return final JSON allocation plan

    ### IMPORTANT: SINGLE BANK BALANCE CALL
    - Call bank_agent EXACTLY ONCE at the beginning
    - Store the result and use it throughout all calculations
    - Do NOT call bank_agent multiple times or retry the call

    ### DECISION LOGIC (NO EXTERNAL DATA)
    - Source of Truth: recommendation_result from previous stock_analysis_agent execution
    - Cash Allocation: Equal split among all Buy recommendations
    - Price Source: current_price field from recommendation_result (NOT live prices)
    - Share Calculation: floor(allocated_amount ÷ current_price)
    - No Hold/Sell Allocations: Set shares_to_buy=0 and total_investment=0.0

    ### CALCULATION EXAMPLE
    Available cash: $10,000
    recommendation_result: [
        {"ticker": "AAPL", "recommendation": "Buy", "current_price": 150.0, ...},
        {"ticker": "GOOGL", "recommendation": "Buy", "current_price": 100.0, ...},
        {"ticker": "MSFT", "recommendation": "Hold", "current_price": 200.0, ...}
    ]

    Buy stocks only: AAPL, GOOGL (ignore MSFT)
    Allocation per Buy stock: $10,000 ÷ 2 = $5,000 each
    AAPL shares: floor($5,000 ÷ $150) = 33 shares = $4,950 invested
    GOOGL shares: floor($5,000 ÷ $100) = 50 shares = $5,000 invested
    Total invested: $9,950, Remaining cash: $50

    ### OUTPUT FORMAT
    First display the input data, then return the allocation in markdown format:

    **Input Analysis:**
    "Received recommendation_result from stock_analysis_agent: [display the full recommendation_result data here]"

    **Final Allocation Plan:**
    Return a markdown formatted report:

    ## Portfolio Allocation Plan

    **Total Available Cash:** $[total_available_cash]
    **Buy Recommendations:** [buy_recommendations_count]
    **Allocation per Stock:** $[allocation_per_stock]
    **Total Invested:** $[total_invested]
    **Remaining Cash:** $[total_remaining_cash]

    **Summary:** [allocation_summary]

    ### Individual Stock Allocations

    #### 1. [TICKER] ([RECOMMENDATION])
    - **Current Price:** $[current_price]
    - **Target Price:** $[target_price]
    - **Allocated Amount:** $[allocated_amount]
    - **Shares to Buy:** [shares_to_buy] shares
    - **Total Investment:** $[total_investment]
    - **Portfolio Weight:** [percentage]%
    - **Rationale:** [rationale]

    ### CRITICAL RULES (STRICTLY ENFORCED)
    - Data Source: Use ONLY recommendation_result context + bank_agent (called once)
    - Single Bank Call: Call bank_agent EXACTLY ONCE - do not retry or call multiple times
    - No External Calls: Do NOT call google_search, get_stock_price, or any internet-based tools
    - No Live Data: Use current_price from recommendation_result (not real-time prices)
    - Calculation Only: This is a mathematical allocation exercise, not live trading
    - Markdown Output: Return ONLY markdown formatted report - no JSON or explanations
    - Complete Coverage: Include ALL stocks from recommendation_result in the allocation report
    - Buy vs Hold/Sell:
        * Buy recommendations: Calculate shares_to_buy and total_investment
        * Hold/Sell recommendations: Set shares_to_buy=0 and total_investment=0.0
    - Price Data: Always include target_price from recommendation_result
    - Share Calculation: Use floor division for whole shares only
    - Cash Tracking: Calculate exact investment amounts and remaining cash

    ### EXAMPLE WITH CONTEXT DATA
    Input recommendation_result: [
        {"ticker": "GOOGL", "recommendation": "Buy", "current_price": 319.95, "target_price": 370.34, ...},
        {"ticker": "TSLA", "recommendation": "Hold", "current_price": 426.58, "target_price": 450.00, ...}
    ]
    Available cash: $10,000 (from bank_agent)

    Processing:
    - Buy stocks: GOOGL only (ignore TSLA Hold)
    - Allocation: $10,000 ÷ 1 = $10,000 to GOOGL
    - GOOGL shares: floor($10,000 ÷ $319.95) = 31 shares = $9,918.45 invested
    - Remaining: $81.55

    Expected Markdown Output:
    ## Portfolio Allocation Plan

    **Total Available Cash:** $10,000.00
    **Buy Recommendations:** 1
    **Allocation per Stock:** $10,000.00
    **Total Invested:** $9,918.45
    **Remaining Cash:** $81.55

    **Summary:** Allocated cash among 1 Buy recommendation

    ### Individual Stock Allocations

    #### 1. GOOGL (Buy)
    - **Current Price:** $319.95
    - **Target Price:** $370.34
    - **Allocated Amount:** $10,000.00
    - **Shares to Buy:** 31 shares
    - **Total Investment:** $9,918.45
    - **Portfolio Weight:** 99.2%
    - **Rationale:** [rationale from recommendation_result]

    #### 2. TSLA (Hold)
    - **Current Price:** $426.58
    - **Target Price:** $450.00
    - **Allocated Amount:** $0.00
    - **Shares to Buy:** 0 shares
    - **Total Investment:** $0.00
    - **Portfolio Weight:** 0.0%
    - **Rationale:** [rationale from recommendation_result]
    """,
    output_key="portfolio_allocation_result"
)

# Root Agent - Complete Investment System
root_agent = SequentialAgent(
    name="InvestmentAdvisorSystem",
    sub_agents=[stock_analysis_agent, portfolio_allocation_agent],
    description="Complete investment advisory system that provides stock recommendations and portfolio allocation."
)



async def main():
    query = "AAPL,GOOGL,TSLA"

    # Create the top-level agent and inject the sub-agents
    runner = InMemoryRunner(agent=root_agent,
                            plugins=[LoggingPlugin()])  # <---- 2. Add the Plugin to the Runner
    response = await runner.run_debug(query)


if __name__ == "__main__":
    asyncio.run(main())
