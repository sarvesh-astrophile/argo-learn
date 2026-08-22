from agno.agent import Agent
from agno.models.openai import OpenAIChat

from ..tools.google_maps import GoogleMapsTools


def build_maps_agent(model: OpenAIChat, google_maps_api_key: str) -> Agent:
    return Agent(
        name="google_map_agent",
        model=model,
        role="Google Maps specialist",
        description="Extracts Google Maps URLs for places using the Google Places API.",
        tools=[GoogleMapsTools(google_maps_api_key=google_maps_api_key)],
        debug_mode=False,
    )
