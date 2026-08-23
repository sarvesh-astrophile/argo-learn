from textwrap import dedent

from .market_analyst import EXPECTED_OUTPUT

DESCRIPTION = dedent("""
You are now connected to the ** Market Analyst Agent ** , the ** Stock Data Agent ** , and the ** DuckDuckGo Agent **

The ** Market Analyst Agent ** will help you generate an initial portfolio proposal based on your input.

The ** Stock Data Agent ** will help you pull current prices, fundamentals, and analyst data for tickers.

The ** DuckDuckGo Agent ** will help you fill in any missing information about companies, funds, or market events identified in the proposal.
""")

INSTRUCTIONS = dedent("""
# ** Portfolio Management Team Instructions **

## 1. Generate the initial portfolio proposal from the market analyst agent based on the user's input.

## 2. Go through the proposed holdings and ensure every ticker has current price and fundamental data included.

## 3. Use the DuckDuckGo Agent to fill any missing information about companies, funds, or market events identified in the proposal.
""")

__all__ = ["DESCRIPTION", "INSTRUCTIONS", "EXPECTED_OUTPUT"]
