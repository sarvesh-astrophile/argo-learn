from textwrap import dedent
import sys

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team import Team
from dotenv import load_dotenv
from agno.db.sqlite import SqliteDb
import os
from pydantic import BaseModel, Field
from agno.tools.exa import ExaTools
from agno.tools.duckduckgo import DuckDuckGoTools
from prompts import system_prompt_travel_agent, instructions, expected_output
from maps_tools import GoogleMapsTools
from rich.prompt import Prompt


_ = load_dotenv()

google_maps_api_key = os.getenv("GOOGLE_MAPS_PLACES_API_KEY")
if not google_maps_api_key:
    raise RuntimeError("API_KEY is not set. Add it to your .env file.")

exa_api_key = os.getenv("EXA_API_KEY")
if not exa_api_key:
    raise RuntimeError("EXA_API_KEY is not set. Add it to your .env file.")

model_api_key = os.getenv("API_KEY")
if not model_api_key:
    raise RuntimeError("API_KEY is not set. Add it to your .env file.")



# Define the Data Models
class MapURL(BaseModel):
    place_name: str = Field(..., description="The name of the place to search for on Google Maps.")
    maps_url: str = Field(..., description="The URL of the Google Maps page for the place.")

class MapURLs(BaseModel):
    urls: list[MapURL] = Field(..., description="A list of MapURL objects.")

class Inputs(BaseModel):
    days: int = Field(..., description="The number of days to plan for.")
    destination: str = Field(..., description="The destination to plan for.")
    trip_date: str = Field(..., description="The date of the trip.")
    budget: float = Field(..., description="The budget for the trip.")

# Define the model
model = OpenAIChat(
    id="deepseek-v4-flash",
    base_url="https://api.deepseek.com",
    api_key=model_api_key,
    # The provider rejects the "developer" role that agno maps "system" to by default
    role_map={
        "system": "system",
        "user": "user",
        "assistant": "assistant",
        "tool": "tool",
        "model": "assistant",
    },
)

# Define the Agents
travel_planning_agent = Agent(
    name="travel_planning_agent",
    model=model,
    db=SqliteDb(db_file="agent.db"),
    tools=[ExaTools(api_key=exa_api_key)],
    description=system_prompt_travel_agent,
    instructions=instructions,
    expected_output=expected_output,
    add_history_to_context=True,
    add_datetime_to_context=True,
    debug_mode=False
)

map_agent = Agent(
    name="google_map_agent",
    model=model,
    description="You are equipped with google maps tools to extract place ID",
    tools=[GoogleMapsTools(google_maps_api_key=google_maps_api_key)],
    debug_mode=False,
)

duckduckgo_agent = Agent(
    name="duckduckgo_agent",
    model=model,
    description="You are equipped with DuckDuckGo tools to help with seraching business info on the web",
    tools=[DuckDuckGoTools()],
    debug_mode=False,
)

team_agents = Team(
    members=[travel_planning_agent, map_agent, duckduckgo_agent],
    model=model,
    add_history_to_context=True,
    add_datetime_to_context=True,
    db=SqliteDb(db_file="agent.db"),
    description= dedent("""
    You are now connected to the ** Travel Planning Agent ** , the ** Google Maps Agent ** , and the ** DuckDuckGo Agent **

    The ** Travel Planning Agent ** will help you generate an initial itinerary based on your input.

    The ** Google Maps Agent ** will help you extract Google Maps URLs for accommodation and activities.

    The ** DuckDuckGo Agent ** will help you fill in any missing information about businesses and landmarks identified in the itinerary.
    """),
    instructions=dedent("""
    # ** Travel Planning Agent Instructions **

    ## 1. Generate the initial itinerary from travel planning agent based on the user's input.

    ## 2. Go through the itinerary and ensure that all locations and landmarks have a Google Maps URL included.

    ## 3. Use the DuckDuckGo Agent to fill any missing information about businesses and landmarks identified in the itinerary.
    """),
    expected_output=expected_output,
    markdown=True,
    show_members_responses=True,
    debug_level=2,
    debug_mode=True,
)


if __name__ == "__main__":
    while True:
        user_prompt = Prompt.ask("User: ")
        if user_prompt.lower() == 'exit' or user_prompt.lower() == 'quit':
            sys.exit('Bye bye! ')

        team_agents.print_response(user_prompt, stream=True)
