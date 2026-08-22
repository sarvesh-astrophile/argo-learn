from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.team import Team

from .config import DEBUG
from .prompts import team as team_prompts


def build_team(members: list[Agent | Team], model: OpenAIChat, db: SqliteDb) -> Team:
    return Team(
        name="travel_planning_team",
        members=members,
        model=model,
        db=db,
        description=team_prompts.DESCRIPTION,
        instructions=team_prompts.INSTRUCTIONS,
        expected_output=team_prompts.EXPECTED_OUTPUT,
        add_history_to_context=True,
        add_datetime_to_context=True,
        markdown=True,
        show_members_responses=True,
        debug_level=2,
        debug_mode=DEBUG,
    )
