import sys

from agno.agent import Agent
from agno.team import Team
from rich.prompt import Prompt

from travel.agents.maps import build_maps_agent
from travel.agents.planner import build_planner_agent
from travel.agents.web_search import build_web_search_agent
from travel.config import get_api_key, get_db, get_model
from travel.team import build_team


def main() -> None:
    model = get_model()
    db = get_db()

    members: list[Agent | Team] = [
        build_planner_agent(model, get_api_key("EXA_API_KEY"), db),
        build_maps_agent(model, get_api_key("GOOGLE_MAPS_PLACES_API_KEY")),
        build_web_search_agent(model),
    ]
    team = build_team(members=members, model=model, db=db)

    while True:
        user_prompt = Prompt.ask("User: ")
        if user_prompt.lower() in ("exit", "quit"):
            sys.exit("Bye bye! ")

        team.print_response(user_prompt, stream=True)  # pyright: ignore[reportUnknownMemberType] - agno's print_response has partially untyped (**kwargs) signature


if __name__ == "__main__":
    main()
