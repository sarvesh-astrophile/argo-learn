from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

from ..prompts import planner


def build_planner_agent(model: OpenAIChat, exa_api_key: str, db: SqliteDb) -> Agent:
    return Agent(
        name="travel_planning_agent",
        model=model,
        db=db,
        tools=[ExaTools(api_key=exa_api_key)],
        role=planner.ROLE,
        description=planner.DESCRIPTION,
        instructions=[planner.SYSTEM_PROMPT, planner.INSTRUCTIONS],
        expected_output=planner.EXPECTED_OUTPUT,
        add_history_to_context=True,
        add_datetime_to_context=True,
        debug_mode=False,
    )
