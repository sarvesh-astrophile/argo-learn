from agno.agent import Agent
from agno.context.mcp import MCPContextProvider
from agno.models.openai import OpenAIChat

from ..prompts import zerodha

KITE_MCP_URL = "https://mcp.kite.trade/mcp"


def build_kite_provider(model: OpenAIChat | None = None) -> MCPContextProvider:
    """Create (unconnected) provider for Zerodha's remote Kite MCP server.

    The caller owns the lifecycle: wire ``await provider.asetup()`` /
    ``await provider.aclose()`` into the app's lifespan. The underlying
    toolkit also reconnects lazily on first tool call if needed.
    """
    return MCPContextProvider(
        server_name="kite",
        id="kite",
        transport="streamable-http",
        url=KITE_MCP_URL,
        model=model,
        timeout_seconds=60,
    )


def build_zerodha_agent(model: OpenAIChat, provider: MCPContextProvider) -> Agent:
    return Agent(
        name="zerodha_agent",
        model=model,
        role=zerodha.ROLE,
        description=zerodha.DESCRIPTION,
        tools=provider.get_tools(),
        instructions=[zerodha.SYSTEM_PROMPT, zerodha.INSTRUCTIONS],
        expected_output=zerodha.EXPECTED_OUTPUT,
        add_history_to_context=True,
        add_datetime_to_context=True,
        debug_mode=False,
    )
