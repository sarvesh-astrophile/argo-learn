from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

from ..prompts import market_analyst


def build_market_analyst_agent(model: OpenAIChat, exa_api_key: str, db: SqliteDb) -> Agent:
    return Agent(
        name="market_analyst_agent",
        model=model,
        db=db,
        tools=[ExaTools(api_key=exa_api_key)],
        role=market_analyst.ROLE,
        description=market_analyst.DESCRIPTION,
        instructions=[market_analyst.SYSTEM_PROMPT, market_analyst.INSTRUCTIONS],
        expected_output=market_analyst.EXPECTED_OUTPUT,
        add_history_to_context=True,
        add_datetime_to_context=True,
        debug_mode=False,
    )
