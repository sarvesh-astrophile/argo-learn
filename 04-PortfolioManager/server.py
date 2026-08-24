from contextlib import asynccontextmanager

from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI

from portfolio.agents.market_analyst import build_market_analyst_agent
from portfolio.agents.stock_data import build_stock_data_agent
from portfolio.agents.web_search import build_web_search_agent
from portfolio.agents.zerodha import build_kite_provider, build_zerodha_agent
from portfolio.config import get_api_key, get_db, get_model
from portfolio.team import build_team


def build_app():
    model = get_model()
    db = get_db()

    kite_provider = build_kite_provider(model=model)
    members = [
        build_market_analyst_agent(model, get_api_key("EXA_API_KEY"), db),
        build_stock_data_agent(model),
        build_web_search_agent(model),
        build_zerodha_agent(model, kite_provider),
    ]
    team = build_team(members=members, model=model, db=db)

    @asynccontextmanager
    async def lifespan(_agent_os: AgentOS):
        await kite_provider.asetup()
        try:
            yield
        finally:
            await kite_provider.aclose()

    agent_os = AgentOS(
        id="portfolio-manager",
        teams=[team],
        interfaces=[AGUI(team=team, prefix="/portfolio")],
        lifespan=lifespan,
    )
    return agent_os.get_app()


app = build_app()

if __name__ == "__main__":
    import uvicorn

    _ = uvicorn.run(app, host="localhost", port=9001)
