# Portfolio Management Team

A multi-agent portfolio manager built with [Agno](https://docs.agno.com).

## Agents

| Agent | Role | Tools |
|-------|------|-------|
| `market_analyst_agent` | Builds the initial portfolio proposal | Exa search |
| `stock_data_agent` | Pulls prices, fundamentals, and analyst data | Custom `PortfolioTools`, Yahoo Finance |
| `duckduckgo_agent` | Fills in missing company/fund/market info | DuckDuckGo |

A `Team` coordinates the three agents: draft the portfolio proposal, attach live
market data, then fill gaps via web search.

## Structure

```
main.py                  # CLI entrypoint
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

