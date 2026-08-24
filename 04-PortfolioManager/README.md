# Portfolio Management Team

A multi-agent portfolio manager built with [Agno](https://docs.agno.com).

## Agents

| Agent | Role | Tools |
|-------|------|-------|
| `market_analyst_agent` | Builds the initial portfolio proposal | Exa search |
| `stock_data_agent` | Pulls prices, fundamentals, and analyst data | Custom `PortfolioTools`, Yahoo Finance |
| `duckduckgo_agent` | Fills in missing company/fund/market info | DuckDuckGo |
| `zerodha_agent` | Fetches your personal Zerodha data via the Kite remote MCP | Kite MCP (`query_kite`) |

A `Team` coordinates the three agents: draft the portfolio proposal, attach live
market data, then fill gaps via web search.

## Structure

```
main.py                  # CLI entrypoint
server.py                # AG-UI server; serves the team incl. zerodha_agent
portfolio/
├── config.py            # env keys, shared model, db, debug flag
├── team.py              # build_team()
├── agents/              # build_*_agent() factories, one file per agent
├── prompts/             # per-agent prompts (role, instructions, expected output)
└── tools/               # custom toolkits (PortfolioTools)
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your API keys
```

## Run

```bash
python main.py
```

Type `exit` or `quit` to stop. Set `AGNO_DEBUG=false` in `.env` to silence
team debug output.

## Zerodha / Kite MCP agent

`zerodha_agent` talks to Zerodha's official remote MCP server at
`https://mcp.kite.trade/mcp` (streamable-http) via Agno's `MCPContextProvider`.
The server's tools are wrapped in a sub-agent exposed as a single
`query_kite` tool, and the agent runs as a member of the team served by
`server.py`. The MCP session is connected/closed in AgentOS's lifespan hook.

**Auth**: no API keys — Kite uses browser OAuth. When the session is not
authenticated, ask anything in chat and the agent calls the `login` tool,
which returns an **authorization URL**. Open it, sign in with your Zerodha
credentials, then retry your question.

```bash
python server.py   # then chat with the team at http://localhost:9001/portfolio/agui
```

### Kite MCP tools

| Category | Tools |
|----------|-------|
| Setup & Auth | `login` |
| Market Data | `get_quotes`, `get_ltp`, `get_ohlc`, `get_historical_data`, `search_instruments` |
| Portfolio & Account | `get_profile`, `get_margins`, `get_holdings`, `get_positions`, `get_mf_holdings` |
| Orders & Trading | `place_order`, `modify_order`, `cancel_order`, `get_orders`, `get_trades`, `get_order_history`, `get_order_trades` |
| GTT Orders | `get_gtts`, `place_gtt_order`, `modify_gtt_order`, `delete_gtt_order` |

Full descriptions live in [`portfolio/prompts/zerodha.py`](portfolio/prompts/zerodha.py).
The agent is read-only by default; order/GTT writes require an explicit,
confirmed instruction.

## Run over AG-UI

```bash
python server.py   # serves http://localhost:9001
```

Exposes the team at `POST /portfolio/agui` speaking the [AG-UI protocol](https://docs.agno.com/agent-os/interfaces/ag-ui/introduction)
(SSE events). Connect any AG-UI-compatible frontend to that URL, e.g.

```bash
npx create-agent-ui@latest   # then point it at http://localhost:9001/portfolio/agui
```

or use CopilotKit / `@ag-ui/client`'s `HttpAgent({ url: ... })`.

