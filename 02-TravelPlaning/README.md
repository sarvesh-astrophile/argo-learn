# Travel Planning Team

A multi-agent travel planner built with [Agno](https://docs.agno.com).

## Agents

| Agent | Role | Tools |
|-------|------|-------|
| `travel_planning_agent` | Builds the initial itinerary | Exa search |
| `google_map_agent` | Resolves Google Maps URLs for places | Custom `GoogleMapsTools` |
| `duckduckgo_agent` | Fills in missing business/landmark info | DuckDuckGo |

A `Team` coordinates the three agents: plan the itinerary, attach Maps URLs,
then fill gaps via web search.

## Structure

```
main.py                # CLI entrypoint
travel/
├── config.py          # env keys, shared model, db, debug flag
├── team.py            # build_team()
├── agents/            # build_*_agent() factories, one file per agent
├── prompts/           # per-agent prompts (role, instructions, expected output)
└── tools/             # custom toolkits (GoogleMapsTools)
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
