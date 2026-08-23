from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools

from ..tools.portfolio import PortfolioTools


def build_stock_data_agent(model: OpenAIChat) -> Agent:
    return Agent(
        name="stock_data_agent",
        model=model,
        role="Market data specialist",
        description="Pulls current prices, fundamentals, analyst recommendations, and company news via Yahoo Finance.",
        tools=[
            YFinanceTools(
                enable_stock_price=True,
                enable_company_info=True,
                enable_analyst_recommendations=True,
                enable_company_news=True,
            ),
            PortfolioTools(),
        ],
        debug_mode=False,
    )
