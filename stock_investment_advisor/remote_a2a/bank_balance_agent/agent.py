from datetime import datetime

from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types


async def bank_balance() -> int:
  """Get available cash balance from bank account.

  Returns:
    Available cash balance in USD (generated from today's date in YYMMDD format).
  """
  today = datetime.now()
  balance = int(today.strftime("%y%m%d"))
  return balance


root_agent = Agent(
    model='gemini-2.5-flash-lite',
    name='bank_balance_agent',
    description='Get available cash in the bank account.',
    instruction="""
      You are a bank balance agent that provides information about available cash in the bank account.
      When asked about bank balance or available cash, call the bank_balance tool to get the current balance.
      The tool returns the available cash amount in USD.
      Always provide the balance information clearly to the user.
    """,
    tools=[
        bank_balance,
    ],
    # planner=BuiltInPlanner(
    #     thinking_config=types.ThinkingConfig(
    #         include_thoughts=True,
    #     ),
    # ),
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
