from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools


def build_web_search_agent(model: OpenAIChat) -> Agent:
    return Agent(
        name="duckduckgo_agent",
        model=model,
        role="Web search specialist",
        description="Searches the web to fill in missing business and landmark information.",
        # "duckduckgo" backend gets rate-limited; "auto" falls back to other engines
        tools=[DuckDuckGoTools(backend="auto")],
        debug_mode=False,
    )
