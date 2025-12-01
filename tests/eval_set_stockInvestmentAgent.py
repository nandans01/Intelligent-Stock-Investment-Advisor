"""
Comprehensive Evaluation Dataset for Stock Investment Agent System
Tests all agents: Root, Stock Recommendation, Stock Data, Stock Analysis, Portfolio Allocation,
Stock News, Stock Price Data, Parallel Data, and Bank Balance
"""

# Evaluation Set Structure:
# Each test case contains:
# - id: Unique identifier
# - category: Test category
# - subcategory: Specific agent or functionality being tested
# - input: User query
# - expected_tickers: Expected ticker symbols to be extracted
# - expected_keys: Keys that should appear in the response
# - validation_criteria: List of criteria to validate the response
# - expected_agents: List of agents that should be invoked
# - notes: Additional context or special considerations

EVAL_SET = [
    # ========== ROOT AGENT TESTS ==========
    {
        "id": "ROOT_001",
        "category": "root_agent",
        "subcategory": "basic_query_routing",
        "input": "Should I invest in Apple?",
        "expected_tickers": ["AAPL"],
        "expected_keys": ["recommendation_result", "portfolio_allocation"],
        "validation_criteria": [
            "Routes to stock_recommendation_agent",
            "Complete end-to-end workflow",
            "Returns formatted final output",
            "Handles user query appropriately"
        ],
        "expected_agents": ["root_agent", "stock_recommendation_agent"],
        "notes": "Root agent query routing test"
    },
    {
        "id": "ROOT_002",
        "category": "root_agent",
        "subcategory": "multi_stock_routing",
        "input": "Compare Tesla and Netflix for my portfolio",
        "expected_tickers": ["TSLA", "NFLX"],
        "expected_keys": ["recommendation_result", "portfolio_allocation"],
        "validation_criteria": [
            "Routes multi-stock query correctly",
            "Maintains conversation context",
            "Provides comprehensive comparison",
            "Proper workflow orchestration"
        ],
        "expected_agents": ["root_agent", "stock_recommendation_agent"],
        "notes": "Multi-stock query routing"
    },
    {
        "id": "ROOT_003",
        "category": "root_agent",
        "subcategory": "error_handling",
        "input": "What's the best investment ever?",
        "expected_tickers": ["UNKNOWN"],
        "expected_keys": [],
        "validation_criteria": [
            "Handles vague queries gracefully",
            "Requests specific company names",
            "Maintains helpful tone",
            "Doesn't provide generic advice"
        ],
        "expected_agents": ["root_agent"],
        "notes": "Root agent error handling"
    },

    # ========== STOCK RECOMMENDATION AGENT TESTS ==========
    {
        "id": "SRA_001",
        "category": "stock_recommendation_agent",
        "subcategory": "ticker_extraction",
        "input": "Should I invest in Apple?",
        "expected_tickers": ["AAPL"],
        "expected_keys": ["recommendation_result", "portfolio_allocation"],
        "validation_criteria": [
            "Extracts AAPL correctly",
            "Calls parallel_data_agent",
            "Calls portfolio_allocation_agent",
            "Returns both recommendations and allocation"
        ],
        "expected_agents": ["stock_recommendation_agent", "parallel_data_agent", "portfolio_allocation_agent"],
        "notes": "Basic stock recommendation workflow test"
    },
    {
        "id": "SRA_002",
        "category": "stock_recommendation_agent",
        "subcategory": "multi_ticker",
        "input": "Compare Apple and Microsoft stocks",
        "expected_tickers": ["AAPL", "MSFT"],
        "expected_keys": ["recommendation_result", "portfolio_allocation"],
        "validation_criteria": [
            "Extracts both AAPL and MSFT",
            "Processes multiple tickers correctly",
            "Returns recommendations for both",
            "Allocates portfolio across both stocks"
        ],
        "expected_agents": ["stock_recommendation_agent", "parallel_data_agent", "portfolio_allocation_agent"],
        "notes": "Multi-ticker stock recommendation test"
    },

    # ========== NEWS AGENT TESTS ==========
    {
        "id": "SNA_001",
        "category": "news_agent",
        "subcategory": "single_ticker_news",
        "input": "AAPL",
        "expected_tickers": ["AAPL"],
        "expected_keys": ["ticker", "stock_news"],
        "validation_criteria": [
            "Fetches news for AAPL",
            "Provides news summary",
            "Returns sentiment analysis",
            "JSON format response"
        ],
        "expected_agents": ["news_agent"],
        "notes": "Single ticker news fetching"
    },
    {
        "id": "SNA_002",
        "category": "news_agent",
        "subcategory": "multi_ticker_news",
        "input": "AAPL,GOOGL",
        "expected_tickers": ["AAPL", "GOOGL"],
        "expected_keys": ["ticker", "stock_news"],
        "validation_criteria": [
            "Fetches news for both tickers",
            "Individual news summaries",
            "Handles multiple ticker input",
            "Consistent output format"
        ],
        "expected_agents": ["news_agent"],
        "notes": "Multi-ticker news fetching"
    },
    {
        "id": "SNA_003",
        "category": "news_agent",
        "subcategory": "invalid_ticker_news",
        "input": "INVALID123",
        "expected_tickers": ["INVALID123"],
        "expected_keys": ["error"],
        "validation_criteria": [
            "Handles invalid ticker gracefully",
            "Returns appropriate error message",
            "Doesn't crash on bad input"
        ],
        "expected_agents": ["news_agent"],
        "notes": "Invalid ticker news handling"
    },

    # ========== STOCK PRICE DATA AGENT TESTS ==========
    {
        "id": "SPDA_001",
        "category": "stock_data_agent",
        "subcategory": "single_ticker_price",
        "input": "AAPL",
        "expected_tickers": ["AAPL"],
        "expected_keys": ["ticker", "current_price", "high_52w", "low_52w", "avg_volume"],
        "validation_criteria": [
            "Calls get_stock_price for AAPL",
            "Returns complete price data",
            "JSON format response",
            "No conversational elements"
        ],
        "expected_agents": ["stock_data_agent"],
        "notes": "Single ticker price data fetching"
    },
    {
        "id": "SPDA_002",
        "category": "stock_data_agent",
        "subcategory": "multi_ticker_price",
        "input": "AAPL,TSLA",
        "expected_tickers": ["AAPL", "TSLA"],
        "expected_keys": ["ticker", "current_price"],
        "validation_criteria": [
            "Fetches price data for both tickers",
            "Individual price objects",
            "Handles comma-separated input",
            "Consistent data structure"
        ],
        "expected_agents": ["stock_data_agent"],
        "notes": "Multi-ticker price data fetching"
    },

    # ========== PARALLEL DATA AGENT TESTS ==========
    {
        "id": "PDA_001",
        "category": "parallel_data_agent",
        "subcategory": "single_ticker_parallel",
        "input": "AAPL",
        "expected_tickers": ["AAPL"],
        "expected_keys": ["stock_news", "recommendation"],
        "validation_criteria": [
            "Calls news_agent",
            "Calls stock_data_agent",
            "Returns combined data structure",
            "Parallel execution efficiency"
        ],
        "expected_agents": ["parallel_data_agent", "news_agent", "stock_data_agent"],
        "notes": "Single ticker parallel data fetching"
    },
    {
        "id": "PDA_002",
        "category": "parallel_data_agent",
        "subcategory": "multi_ticker_parallel",
        "input": "AAPL,GOOGL,TSLA",
        "expected_tickers": ["AAPL", "GOOGL", "TSLA"],
        "expected_keys": ["stock_news", "recommendation"],
        "validation_criteria": [
            "Processes all tickers in parallel",
            "Combines news and price data",
            "Maintains data consistency",
            "Efficient parallel processing"
        ],
        "expected_agents": ["parallel_data_agent", "news_agent", "stock_data_agent"],
        "notes": "Multi-ticker parallel data fetching"
    },

    # ========== EXISTING STOCK DATA AGENT TESTS ==========
    {
        "id": "SDA_001",
        "category": "stock_data_agent",
        "subcategory": "single_ticker",
        "input": "AAPL",
        "expected_tickers": ["AAPL"],
        "expected_keys": ["ticker", "current_price", "high_52w", "low_52w", "avg_volume"],
        "validation_criteria": [
            "Calls get_stock_price for AAPL",
            "Returns price data immediately",
            "No investment advice disclaimers",
            "JSON format response"
        ],
        "expected_agents": ["stock_data_agent"],
        "notes": "Direct stock data fetching test"
    },
    {
        "id": "SDA_002",
        "category": "stock_data_agent",
        "subcategory": "multi_ticker",
        "input": "GOOGL,TSLA",
        "expected_tickers": ["GOOGL", "TSLA"],
        "expected_keys": ["ticker", "current_price", "high_52w", "low_52w", "avg_volume"],
        "validation_criteria": [
            "Calls get_stock_price for both tickers",
            "Returns data for both stocks",
            "Processes comma-separated input",
            "No conversational responses"
        ],
        "expected_agents": ["stock_data_agent"],
        "notes": "Multi-ticker data fetching"
    },
    {
        "id": "SDA_003",
        "category": "stock_data_agent",
        "subcategory": "invalid_ticker",
        "input": "XYZ123INVALID",
        "expected_tickers": ["XYZ123INVALID"],
        "expected_keys": ["error"],
        "validation_criteria": [
            "Attempts to fetch invalid ticker",
            "Returns error gracefully"
        ],
        "expected_agents": ["stock_data_agent"],
        "notes": "Invalid ticker handling"
    },

    # ========== STOCK ANALYSIS AGENT TESTS ==========
    {
        "id": "SAA_001",
        "category": "stock_analysis_agent",
        "subcategory": "buy_recommendation",
        "input": "Analyze AAPL stock data",
        "expected_tickers": ["AAPL"],
        "expected_keys": ["ticker", "recommendation", "current_price", "target_price", "rationale"],
        "validation_criteria": [
            "Provides Buy/Hold/Sell recommendation",
            "Includes current price from data",
            "Sets realistic target price",
            "Gives 2-3 sentence rationale",
            "Uses only provided stock data"
        ],
        "expected_agents": ["stock_analysis_agent"],
        "notes": "Stock analysis with recommendation generation"
    },
    {
        "id": "SAA_002",
        "category": "stock_analysis_agent",
        "subcategory": "multi_stock_analysis",
        "input": "Analyze GOOGL and META stock data",
        "expected_tickers": ["GOOGL", "META"],
        "expected_keys": ["ticker", "recommendation", "current_price", "target_price", "rationale"],
        "validation_criteria": [
            "Provides recommendations for both stocks",
            "Individual target prices for each",
            "Separate rationales for each stock",
            "JSON array format"
        ],
        "expected_agents": ["stock_analysis_agent"],
        "notes": "Multi-stock analysis test"
    },
    {
        "id": "SAA_003",
        "category": "stock_analysis_agent",
        "subcategory": "hold_recommendation",
        "input": "Analyze TSLA with neutral sentiment",
        "expected_tickers": ["TSLA"],
        "expected_keys": ["ticker", "recommendation", "current_price", "target_price", "rationale"],
        "validation_criteria": [
            "Can provide Hold recommendation",
            "Justifies neutral stance",
            "Conservative target price",
            "Risk-aware rationale"
        ],
        "expected_agents": ["stock_analysis_agent"],
        "notes": "Testing Hold recommendation capability"
    },

    # ========== PORTFOLIO ALLOCATION AGENT TESTS ==========
    {
        "id": "PAA_001",
        "category": "portfolio_allocation_agent",
        "subcategory": "single_buy_allocation",
        "input": "Allocate portfolio with AAPL Buy recommendation",
        "expected_tickers": ["AAPL"],
        "expected_keys": ["total_available_cash", "shares_to_buy", "total_investment", "portfolio_weight"],
        "validation_criteria": [
            "Calls bank_agent exactly once",
            "Allocates full cash to Buy recommendation",
            "Calculates correct share quantities",
            "Shows investment amounts and portfolio weight",
            "Displays recommendation_result input data"
        ],
        "expected_agents": ["portfolio_allocation_agent", "bank_agent"],
        "notes": "Single Buy stock allocation"
    },
    {
        "id": "PAA_002",
        "category": "portfolio_allocation_agent",
        "subcategory": "multi_buy_allocation",
        "input": "Allocate portfolio with AAPL and GOOGL Buy recommendations",
        "expected_tickers": ["AAPL", "GOOGL"],
        "expected_keys": ["Total Available Cash", "Shares to Buy", "Total Investment", "Portfolio Weight"],
        "validation_criteria": [
            "Calls bank_agent exactly once",
            "Splits cash equally between Buy stocks",
            "Calculates shares for both stocks",
            "Shows individual allocations",
            "Remaining cash calculation"
        ],
        "expected_agents": ["portfolio_allocation_agent", "bank_agent"],
        "notes": "Multi-Buy stock allocation"
    },
    {
        "id": "PAA_003",
        "category": "portfolio_allocation_agent",
        "subcategory": "mixed_recommendations",
        "input": "Allocate portfolio with AAPL Buy and TSLA Hold recommendations",
        "expected_tickers": ["AAPL", "TSLA"],
        "expected_keys": ["Total Available Cash", "Buy Recommendations", "Total Investment"],
        "validation_criteria": [
            "Allocates cash only to Buy recommendations",
            "Shows 0 allocation for Hold stocks"

        ],
        "expected_agents": ["portfolio_allocation_agent", "bank_agent"],
        "notes": "Mixed Buy/Hold allocation test"
    },
    {
        "id": "PAA_004",
        "category": "portfolio_allocation_agent",
        "subcategory": "no_buy_recommendations",
        "input": "Allocate portfolio with all Hold/Sell recommendations",
        "expected_tickers": ["TSLA", "NFLX"],
        "expected_keys": ["Total Available Cash", "Total Investment"],
        "validation_criteria": [
            "Shows available cash but no investments",
            "All allocations are $0",
            "All share quantities are 0",
            "Explains no Buy recommendations available"
        ],
        "expected_agents": ["portfolio_allocation_agent", "bank_agent"],
        "notes": "No Buy recommendations scenario"
    },
    {
        "id": "PAA_005",
        "category": "portfolio_allocation_agent",
        "subcategory": "markdown_output",
        "input": "Provide markdown allocation report",
        "expected_tickers": ["AAPL"],
        "expected_keys": ["## Portfolio Allocation Plan", "### Individual Stock Allocations"],
        "validation_criteria": [
            "Returns markdown formatted report",
            "Uses proper markdown headers",
            "Shows financial data with $ formatting",
            "Includes rationale from recommendations"
        ],
        "expected_agents": ["portfolio_allocation_agent", "bank_agent"],
        "notes": "Markdown formatting test"
    },

    # ========== BANK BALANCE AGENT TESTS ==========
    {
        "id": "BBA_001",
        "category": "bank_agent",
        "subcategory": "balance_retrieval",
        "input": "What's my bank balance?",
        "expected_tickers": [],
        "expected_keys": ["balance", "cash"],
        "validation_criteria": [
            "Returns date-based balance (YYMMDD format)",
            "Value between 100000-300000 range",
            "Provides clear balance information"
        ],
        "expected_agents": ["bank_agent"],
        "notes": "Direct bank balance query"
    },
    {
        "id": "BBA_002",
        "category": "bank_agent",
        "subcategory": "available_cash",
        "input": "How much cash do I have available?",
        "expected_tickers": [],
        "expected_keys": ["available", "cash"],
        "validation_criteria": [
            "Returns current available cash",
            "Uses bank_balance function",
            "Same value for same date"
        ],
        "expected_agents": ["bank_agent"],
        "notes": "Available cash inquiry"
    },

    # ========== END-TO-END INTEGRATION TESTS (UPDATED) ==========
    {
        "id": "E2E_001",
        "category": "end_to_end",
        "subcategory": "full_workflow_single",
        "input": "Should I invest in Apple?",
        "expected_tickers": ["AAPL"],
        "expected_keys": ["recommendation_result", "portfolio_allocation"],
        "validation_criteria": [
            "Complete workflow execution",
            "Stock data fetched successfully",
            "Investment recommendation provided",
            "Portfolio allocation calculated",
            "Bank balance retrieved",
            "Markdown formatted final output"
        ],
        "expected_agents": ["root_agent", "stock_recommendation_agent", "parallel_data_agent", "news_agent", "stock_data_agent", "portfolio_allocation_agent", "bank_agent"],
        "notes": "Full end-to-end single stock workflow"
    },

    # ========== INTEGRATION TESTS ==========
    {
        "id": "INT_001",
        "category": "integration",
        "subcategory": "parallel_data_flow",
        "input": "Analyze Apple with complete data pipeline",
        "expected_tickers": ["AAPL"],
        "expected_keys": ["stock_news", "stock_price_data", "recommendation_result"],
        "validation_criteria": [
            "Parallel data agent coordinates properly",
            "News and price data both fetched",
            "Data flows to recommendation agent",
            "No data inconsistencies"
        ],
        "expected_agents": ["parallel_data_agent", "news_agent", "stock_data_agent", "stock_recommendation_agent"],
        "notes": "Integration test for parallel data flow"
    },

    {
        "id": "INT_002",
        "category": "integration",
        "subcategory": "recommendation_to_allocation",
        "input": "Get recommendation and allocation for Microsoft",
        "expected_tickers": ["MSFT"],
        "expected_keys": ["recommendation_result", "portfolio_allocation"],
        "validation_criteria": [
            "Recommendation flows to allocation properly",
            "Buy recommendations get cash allocation",
            "Data consistency maintained",
            "Complete integration chain"
        ],
        "expected_agents": ["stock_recommendation_agent", "portfolio_allocation_agent", "bank_agent"],
        "notes": "Integration test for recommendation to allocation flow"
    }
]


# Updated validation functions to include new agents
def validate_response(response: str, test_case: dict) -> dict:
    """
    Enhanced validation function for comprehensive agent testing
    """
    results = {
        "test_id": test_case["id"],
        "category": test_case["category"],
        "subcategory": test_case["subcategory"],
        "input": test_case["input"],
        "passed": True,
        "failed_criteria": [],
        "details": {},
        "agent_validation": {}
    }

    response_lower = response.lower()

    # 1. Ticker Validation
    tickers_found = []
    for ticker in test_case["expected_tickers"]:
        if ticker == "UNKNOWN":
            # Special handling for unknown/invalid cases
            if any(keyword in response_lower for keyword in ["unknown", "invalid", "not found", "specify"]):
                tickers_found.append("UNKNOWN")
        else:
            if ticker.lower() in response_lower:
                tickers_found.append(ticker)

    results["details"]["tickers_found"] = tickers_found
    results["details"]["expected_tickers"] = test_case["expected_tickers"]

    # Check ticker extraction accuracy
    if test_case["expected_tickers"] != ["UNKNOWN"]:
        expected_set = set(test_case["expected_tickers"])
        found_set = set(tickers_found)
        if expected_set != found_set:
            results["passed"] = False
            results["failed_criteria"].append(f"Ticker mismatch: expected {expected_set}, found {found_set}")

    # 2. Expected Keys Validation
    keys_found = []
    for key in test_case["expected_keys"]:
        if key.lower() in response_lower or f'"{key}"' in response or f"'{key}'" in response:
            keys_found.append(key)

    results["details"]["keys_found"] = keys_found
    missing_keys = set(test_case["expected_keys"]) - set(keys_found)
    if missing_keys:
        results["passed"] = False
        results["failed_criteria"].append(f"Missing keys: {missing_keys}")

    # 3. Agent-Specific Validation
    subcategory = test_case["subcategory"]

    if "stock_data_agent" in test_case["category"]:
        results["agent_validation"]["stock_data"] = validate_stock_data_agent(response, test_case)

    elif "stock_analysis_agent" in test_case["category"]:
        results["agent_validation"]["stock_analysis"] = validate_stock_analysis_agent(response, test_case)

    elif "portfolio_allocation_agent" in test_case["category"]:
        results["agent_validation"]["portfolio_allocation"] = validate_portfolio_allocation_agent(response, test_case)

    elif "bank_agent" in test_case["category"]:
        results["agent_validation"]["bank_agent"] = validate_bank_agent(response, test_case)

    elif "end_to_end" in test_case["category"]:
        results["agent_validation"]["end_to_end"] = validate_end_to_end(response, test_case)

    # Add validation for new agents
    if "root_agent" in test_case["category"]:
        results["agent_validation"]["root_agent"] = validate_root_agent(response, test_case)

    elif "news_agent" in test_case["category"]:
        results["agent_validation"]["news"] = validate_news_agent(response, test_case)

    elif "stock_data_agent" in test_case["category"]:
        results["agent_validation"]["stock_data"] = validate_stock_data_agent(response, test_case)

    elif "parallel_data_agent" in test_case["category"]:
        results["agent_validation"]["parallel_data"] = validate_parallel_data_agent(response, test_case)

    # 4. Validation Criteria Checks
    for criterion in test_case["validation_criteria"]:
        if not check_validation_criterion(response, criterion):
            results["passed"] = False
            results["failed_criteria"].append(f"Failed criterion: {criterion}")

    # 5. Overall Agent Validation Check
    agent_validations = results["agent_validation"]
    for agent_type, validation_result in agent_validations.items():
        if not validation_result.get("passed", True):
            results["passed"] = False
            results["failed_criteria"].extend(validation_result.get("failures", []))

    return results


def validate_stock_data_agent(response: str, test_case: dict) -> dict:
    """Validate stock data agent specific behavior"""
    result = {"passed": True, "failures": []}
    response_lower = response.lower()

    # Check for immediate data fetching (no conversation)
    conversation_indicators = [
        "would you like me to", "should i", "what do you think",
        "i cannot provide investment advice", "let me know"
    ]

    if any(indicator in response_lower for indicator in conversation_indicators):
        result["passed"] = False
        result["failures"].append("Stock data agent engaging in conversation instead of fetching data")

    # Only check for required price data fields if ticker is valid (not error case)
    is_error_case = (
        test_case.get("subcategory") == "invalid_ticker" or
        "error" in test_case.get("expected_keys", []) or
        any("invalid" in ticker.lower() for ticker in test_case.get("expected_tickers", []))
    )

    if not is_error_case:
        # Check for required price data fields only for valid tickers
        required_fields = ["current_price", "high_52w", "low_52w", "avg_volume"]
        for field in required_fields:
            if field not in response_lower and field.replace("_", " ") not in response_lower:
                result["passed"] = False
                result["failures"].append(f"Missing required price field: {field}")
    else:
        # For error cases, check that error is handled gracefully
        error_indicators = ["error", "invalid", "not found", "failed"]
        if not any(indicator in response_lower for indicator in error_indicators):
            result["passed"] = False
            result["failures"].append("Invalid ticker should return error indication")

    return result


def validate_stock_analysis_agent(response: str, test_case: dict) -> dict:
    """Validate stock analysis agent specific behavior"""
    result = {"passed": True, "failures": []}
    response_lower = response.lower()

    # Check for recommendation
    has_recommendation = any(rec in response_lower for rec in ["buy", "sell", "hold", "strong buy", "strong sell"])
    if not has_recommendation:
        result["passed"] = False
        result["failures"].append("Missing investment recommendation")

    # Check for target price
    if "target_price" not in response_lower and "target price" not in response_lower:
        result["passed"] = False
        result["failures"].append("Missing target price")

    # Check for rationale
    if "rationale" not in response_lower:
        result["passed"] = False
        result["failures"].append("Missing investment rationale")

    return result


def validate_portfolio_allocation_agent(response: str, test_case: dict) -> dict:
    """Validate portfolio allocation agent specific behavior"""
    result = {"passed": True, "failures": []}
    response_lower = response.lower()

    # Check for markdown formatting
    markdown_indicators = ["##", "###", "**", "-"]
    if not any(indicator in response for indicator in markdown_indicators):
        result["passed"] = False
        result["failures"].append("Response not in markdown format")

    # Check for allocation fields
    allocation_fields = ["total_available_cash", "shares_to_buy", "total_investment"]
    for field in allocation_fields:
        if field not in response_lower and field.replace("_", " ") not in response_lower:
            result["passed"] = False
            result["failures"].append(f"Missing allocation field: {field}")

    # Check for bank balance call indication
    if "bank" not in response_lower and "balance" not in response_lower:
        result["passed"] = False
        result["failures"].append("No indication of bank balance retrieval")

    return result


def validate_bank_agent(response: str, test_case: dict) -> dict:
    """Validate bank agent specific behavior"""
    result = {"passed": True, "failures": []}
    response_lower = response.lower()

    # Check for balance information
    balance_indicators = ["balance", "cash", "available", "$"]
    if not any(indicator in response_lower for indicator in balance_indicators):
        result["passed"] = False
        result["failures"].append("No balance information provided")

    # Check for reasonable balance amount (date-based should be 6-digit number)
    import re
    balance_pattern = r'\$?(\d{6,})'
    if not re.search(balance_pattern, response):
        result["passed"] = False
        result["failures"].append("No valid balance amount found")

    return result


def validate_end_to_end(response: str, test_case: dict) -> dict:
    """Validate end-to-end workflow"""
    result = {"passed": True, "failures": []}
    response_lower = response.lower()

    # Check for both recommendations and allocation sections
    if "recommendation" not in response_lower:
        result["passed"] = False
        result["failures"].append("Missing stock recommendations section")

    if "allocation" not in response_lower and "portfolio" not in response_lower:
        result["passed"] = False
        result["failures"].append("Missing portfolio allocation section")


    return result


def validate_root_agent(response: str, test_case: dict) -> dict:
    """Validate root agent specific behavior"""
    result = {"passed": True, "failures": []}
    response_lower = response.lower()

    # Check for proper routing behavior
    if test_case["subcategory"] == "basic_query_routing":
        if "recommendation" not in response_lower:
            result["passed"] = False
            result["failures"].append("Root agent should route to recommendation workflow")

    # Check for user-friendly responses
    #if "error" in response_lower and test_case["subcategory"] != "error_handling":
    #    result["passed"] = False
    #    result["failures"].append("Root agent showing errors instead of user-friendly responses")

    return result


def validate_news_agent(response: str, test_case: dict) -> dict:
    """Validate news agent specific behavior"""
    result = {"passed": True, "failures": []}
    response_lower = response.lower()

    # Check for news content
    news_indicators = ["news", "summary", "sentiment", "company", "announcement"]
    if not any(indicator in response_lower for indicator in news_indicators):
        result["passed"] = False
        result["failures"].append("Missing news content indicators")

    # Check for structured output
    if test_case["subcategory"] != "invalid_ticker_news":
        if "ticker" not in response_lower:
            result["passed"] = False
            result["failures"].append("Missing ticker in news response")

    return result


def validate_parallel_data_agent(response: str, test_case: dict) -> dict:
    """Validate parallel data agent specific behavior"""
    result = {"passed": True, "failures": []}
    response_lower = response.lower()

    # Check for both news and price data
    if "stock_news" not in response_lower:
        result["passed"] = False
        result["failures"].append("Missing stock_news in parallel data response")

    if "recommendation" not in response_lower:
        result["passed"] = False
        result["failures"].append("Missing recommendation in parallel data response")

    return result


def check_validation_criterion(response: str, criterion: str) -> bool:
    """Check individual validation criterion"""
    response_lower = response.lower()
    criterion_lower = criterion.lower()

    # Keyword-based validation logic
    if "recommendation" in criterion_lower:
        return any(keyword in response_lower for keyword in ["buy", "sell", "hold"])

    if "current_price" in criterion_lower:
        return "current_price" in response_lower or "current price" in response_lower

    if "target_price" in criterion_lower:
        return "target_price" in response_lower or "target price" in response_lower

    if "rationale" in criterion_lower:
        return "rationale" in response_lower

    if "markdown" in criterion_lower:
        return any(marker in response for marker in ["##", "###", "**", "-"])

    if "bank_agent" in criterion_lower or "bank balance" in criterion_lower:
        return "bank" in response_lower or "balance" in response_lower

    if "cash allocation" in criterion_lower:
        return "cash" in response_lower and ("allocation" in response_lower or "allocated" in response_lower)

    # Default: check if key phrases from criterion exist in response
    key_phrases = criterion_lower.split()
    return any(phrase in response_lower for phrase in key_phrases if len(phrase) > 3)


def get_eval_set_by_category(category: str = None):
    """Get evaluation set filtered by category"""
    if category is None:
        return EVAL_SET
    return [test for test in EVAL_SET if test["category"] == category]


def get_eval_set_by_agent(agent_name: str):
    """Get evaluation set filtered by specific agent"""
    return [test for test in EVAL_SET if agent_name in test.get("expected_agents", [])]


def get_eval_set_statistics():
    """Get comprehensive statistics about the evaluation set"""
    categories = {}
    subcategories = {}
    agents = {}

    for test in EVAL_SET:
        # Category stats
        cat = test["category"]
        categories[cat] = categories.get(cat, 0) + 1

        # Subcategory stats
        subcat = test["subcategory"]
        subcategories[subcat] = subcategories.get(subcat, 0) + 1

        # Agent stats
        for agent in test.get("expected_agents", []):
            agents[agent] = agents.get(agent, 0) + 1

    return {
        "total_tests": len(EVAL_SET),
        "categories": categories,
        "subcategories": subcategories,
        "agents_tested": agents,
        "category_breakdown": {
            cat: f"{count} tests ({count/len(EVAL_SET)*100:.1f}%)"
            for cat, count in categories.items()
        },
        "agent_coverage": {
            agent: f"{count} tests"
            for agent, count in agents.items()
        }
    }


if __name__ == "__main__":
    print("=" * 80)
    print("COMPREHENSIVE STOCK INVESTMENT AGENT SYSTEM - EVALUATION SET")
    print("=" * 80)

    stats = get_eval_set_statistics()
    print(f"\nTotal Test Cases: {stats['total_tests']}")

    print(f"\nAgent Coverage:")
    for agent, coverage in stats["agent_coverage"].items():
        print(f"  - {agent}: {coverage}")

    print(f"\nCategory Breakdown:")
    for category, breakdown in stats["category_breakdown"].items():
        print(f"  - {category}: {breakdown}")

    print("\n" + "=" * 80)
    print("SAMPLE TEST CASES BY AGENT")
    print("=" * 80)

    # Show sample from each agent category
    agent_samples = {}
    for test in EVAL_SET:
        category = test["category"]
        if category not in agent_samples:
            agent_samples[category] = test

    for category, test in agent_samples.items():
        print(f"\n[{test['category'].upper()}] {test['id']} - {test['subcategory']}")
        print(f"Input: {test['input']}")
        print(f"Expected Agents: {', '.join(test.get('expected_agents', ['None']))}")
        print(f"Validation Criteria: {len(test['validation_criteria'])} checks")

    print("\n" + "=" * 80)
