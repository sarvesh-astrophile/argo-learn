import os

from agno.agent import Agent
from agno.models.openai import OpenResponses
from dotenv import load_dotenv
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from agno.team import Team

_ = load_dotenv()

api_key = os.getenv("API_KEY")
if not api_key:
    raise RuntimeError("API_KEY is not set. Add it to your .env file.")

model = OpenResponses(
    id="nemotron-3-ultra-free",
    base_url="https://opencode.ai/zen/v1",
    api_key=api_key,
)

web_agent = Agent(
    name="Web Agent",
    tools=[DuckDuckGoTools()],
    role="You are a web agent that can search the web for information.",
    instructions="Always include the source in your responses.",
    markdown=True,
    model=model,
)

finance_agent = Agent(
    tools=[YFinanceTools(all=True)],
    description="You are an investment analyst that researches stock prices, analyst recommendations, and stock fundamentals.",
    instructions=["Format your response using markdown and use tables to display data where possible."],
    model=model,
)

agent_team = Team(
    members=[web_agent, finance_agent],
    model=model,
)

agent_team.print_response("Who won the latest cricket match? india vs")
