# Refactoring Report: Travel Planning Multi-Agent Project

**Scope:** `02-TravelPlaning/`
**Goal:** Turn a single-script prototype into a well-organized, type-safe multi-agent
project following Agno best practices.
**Result:** `basedpyright` → 0 errors, 0 warnings; team builds and runs identically.

---

## 1. Before vs. After

### Before

```
02-TravelPlaning/
├── travel-agent.py    # 131 lines doing EVERYTHING
├── maps_tools.py      # custom toolkit
├── prompts.py         # prompts for all agents in one file
├── requirements.txt
└── __pycache__/
```

### After

```
02-TravelPlaning/
├── .env.example          # required API keys, documented
├── README.md             # setup + run instructions
├── requirements.txt      # complete dependencies
├── main.py               # CLI entrypoint only
└── travel/               # importable package
    ├── __init__.py
    ├── config.py         # env keys, shared model, db, debug flag
    ├── team.py           # build_team()
    ├── agents/
    │   ├── __init__.py
    │   ├── planner.py    # build_planner_agent()
    │   ├── maps.py       # build_maps_agent()
    │   └── web_search.py # build_web_search_agent()
    ├── prompts/
    │   ├── __init__.py
    │   ├── planner.py    # planner prompts only
    │   └── team.py       # team prompts only
    └── tools/
        ├── __init__.py
        └── google_maps.py # GoogleMapsTools (logic unchanged)
```

Plus `pyrightconfig.json` at the repo root for type-checker import resolution.

---

## 2. Problems Found and How They Were Fixed

### 2.1 The "god file" — `travel-agent.py`

**Problem:** One file contained 5 unrelated concerns:

1. Environment/config loading and validation
2. Pydantic data models
3. Model (LLM client) configuration
4. Agent and Team definitions
5. The interactive CLI loop

It also had a **hyphen in the filename** (`travel-agent.py`), which makes it impossible
to `import travel-agent` — Python module names must be valid identifiers.

**Why it matters:** In agent projects the entrypoint changes constantly (CLI today,
Streamlit/FastAPI tomorrow), while agents and tools stay stable. Mixing them means
every UI change risks breaking agent definitions, and agents can't be reused or
unit-tested without running the whole CLI.

**Fix:** Split by responsibility:

- `main.py` — only the CLI loop (`Prompt.ask`, `exit`/`quit`, `print_response`)
- `travel/config.py` — all configuration
- `travel/agents/*.py` — one factory per agent
- `travel/team.py` — team assembly

### 2.2 No central configuration

**Problem:** API keys were read and validated at import time at the top of the
entry script, and the model was constructed inline:

```python
google_maps_api_key = os.getenv("GOOGLE_MAPS_PLACES_API_KEY")
if not google_maps_api_key:
    raise RuntimeError(...)
```

**Why it matters:** Import-time side effects make modules un-importable without a
fully configured environment — you can't even run a type check or a unit test.
Scattered validation also produces inconsistent error messages.

**Fix:** `travel/config.py` exposes three small functions:

```python
def get_api_key(name: str) -> str        # validated lookup with clear error
def get_model() -> OpenAIChat            # one shared model definition
def get_db() -> SqliteDb                 # one shared db definition
DEBUG = os.getenv("AGNO_DEBUG", "true").lower() == "true"
```

Keys are now fetched **lazily** (when `main()` runs, not at import), and the
DeepSeek-specific `role_map` workaround lives in exactly one place.

### 2.3 Misuse of Agno's `description` field

**Problem:** The full "Elite Travel Planning Expert" system prompt was passed as
`description=`:

```python
travel_planning_agent = Agent(
    description=system_prompt_travel_agent,   # ~20 lines of markdown!
    instructions=instructions,
    ...
)
```

**Why it matters (Agno semantics):**

| Field | Purpose | Right content |
|-------|---------|---------------|
| `name` | Identifier | `"travel_planning_agent"` |
| `role` | One-line identity | `"Elite Travel Planning Expert"` |
| `description` | Short summary of what the agent does | 1–2 sentences |
| `instructions` | Detailed behavior/rules (str or list of str) | The long markdown |

`description` is also shown to the **Team leader** when it decides which member to
delegate to — a wall of markdown there actively hurts routing quality.

**Fix:**

```python
Agent(
    name="travel_planning_agent",
    role=planner.ROLE,                                  # one line
    description=planner.DESCRIPTION,                    # one sentence
    instructions=[planner.SYSTEM_PROMPT, planner.INSTRUCTIONS],  # the details
)
```

Note `instructions` accepts a **list of strings** — Agno joins them. This keeps the
persona (`SYSTEM_PROMPT`) separate from the methodology (`INSTRUCTIONS`) without
string concatenation.

### 2.4 Dead code

**Problem:** `MapURL`, `MapURLs`, and `Inputs` Pydantic models were defined but
never used anywhere.

**Why it matters:** Dead code misleads readers into thinking structured output is
implemented. In Agno, the correct mechanism is `output_schema=YourModel` on the
`Agent` or `Team` — if those models were ever needed, that's where they'd be wired in.

**Fix:** Deleted. (Reintroduce later via `output_schema=` if structured output is
actually wanted.)

### 2.5 Monolithic prompts file

**Problem:** `prompts.py` mixed the planner agent's persona, its methodology, its
expected output, AND (implicitly) the team's prompts, which were inline in
`travel-agent.py`.

**Fix:** Prompts now live next to their owner:

- `travel/prompts/planner.py` — `ROLE`, `DESCRIPTION`, `SYSTEM_PROMPT`,
  `INSTRUCTIONS`, `EXPECTED_OUTPUT` (named constants instead of long variable names)
- `travel/prompts/team.py` — team `DESCRIPTION` / `INSTRUCTIONS`, reusing the
  planner's `EXPECTED_OUTPUT` via import (single source of truth)

**Lesson:** when a prompt needs editing, you now know exactly which file to open,
and each prompt file is diff-friendly in git.

### 2.6 Agents defined as import-time globals

**Problem:** Agents and the team were module-level objects constructed at import.

**Fix:** Factory functions with **dependency injection**:

```python
def build_planner_agent(model: OpenAIChat, exa_api_key: str, db: SqliteDb) -> Agent: ...
def build_maps_agent(model: OpenAIChat, google_maps_api_key: str) -> Agent: ...
def build_web_search_agent(model: OpenAIChat) -> Agent: ...
def build_team(members: list[Agent | Team], model: OpenAIChat, db: SqliteDb) -> Team: ...
```

**Why it matters:**

- Dependencies (`model`, `db`, keys) are explicit in the signature — no hidden globals
- One shared `model` and `SqliteDb` instance are created once in `main()` and injected
  (matches Agno's own team examples, where members share the leader's model)
- Each agent can be built in isolation in a test with a mock model/db

### 2.7 Incomplete requirements and undocumented secrets

**Problem:** `requirements.txt` was missing `python-dotenv` and `rich`, both of
which were imported. No `.env.example` existed, so a new developer couldn't know
the project needs **three** keys: `API_KEY`, `EXA_API_KEY`,
`GOOGLE_MAPS_PLACES_API_KEY`.

**Fix:** Completed `requirements.txt`; added `.env.example` documenting each key
plus the optional `AGNO_DEBUG` toggle; added a `README.md` with a structure map,
agent table, and setup/run instructions.

---

## 3. Type-Checking Fixes (basedpyright)

Final result: **0 errors, 0 warnings**. Three categories were fixed:

### 3.1 Implicit relative imports — 13 errors (`reportImplicitRelativeImport`)

**Error:** `from travel.prompts import planner` inside the package was flagged as an
implicit relative import.

**Why it happened:** basedpyright runs from the workspace root. `02-TravelPlaning/`
cannot be a Python package (the hyphen is an invalid identifier), so the checker had
no import root where `travel` is a top-level package — it assumed the imports were
relative to each file's location, which silently breaks when a file is imported as a
module rather than run as a script.

**Fixes (two layers):**

1. **Explicit relative imports inside the package** — the correct pattern for
   intra-package references, making the package location-independent:

   ```python
   from ..prompts import planner          # in travel/agents/planner.py
   from ..tools.google_maps import ...    # in travel/agents/maps.py
   from .planner import build_...          # in travel/agents/__init__.py
   ```

2. **`pyrightconfig.json` at repo root** — declares each project folder as an
   execution environment so `main.py`'s script-style absolute imports resolve:

   ```json
   { "executionEnvironments": [
       { "root": "01-BasicAgents" },
       { "root": "02-TravelPlaning" } ] }
   ```

**Lesson:** *inside a package → relative imports; entrypoint script → absolute
imports + declared execution environment.*

### 3.2 Invariant generics — 1 error (`reportArgumentType`)

**Error:** `list[Agent]` could not be passed to `Team(members: List[Agent | Team])`.

**Why it happened:** `list[T]` is **invariant** in `T`. Even though every `Agent`
is a valid `Agent | Team`, a `list[Agent]` is not a `list[Agent | Team]` — because
the receiving function could legally append a `Team` into it, corrupting the
caller's list. (`Sequence` is covariant and would accept it, but Agno's parameter
is typed `List`.)

**Fix:** Agree on the wider type at both ends:

```python
# travel/team.py
def build_team(members: list[Agent | Team], ...) -> Team: ...

# main.py
members: list[Agent | Team] = [
    build_planner_agent(...),
    build_maps_agent(...),
    build_web_search_agent(...),
]
```

**Lesson:** when a function stores or mutates a list you pass in, annotate the
parameter with the union the callee expects, and annotate the caller's variable the
same way.

### 3.3 Partially unknown library type — 1 warning (`reportUnknownMemberType`)

**Warning:** `team.print_response(...)` — Agno's signature contains `**kwargs: Any`
and untyped generics, so its type is "partially unknown".

**Why it's not our bug:** this comes from the library's type stubs, not our code.

**Fix:** targeted suppression with a reason, rather than weakening the whole config:

```python
team.print_response(user_prompt, stream=True)  # pyright: ignore[reportUnknownMemberType] - agno's print_response has partially untyped (**kwargs) signature
```

**Lesson:** suppress at the call site with a comment explaining why; never disable a
rule project-wide to silence one library.

---

## 4. Agno Best Practices Applied (Checklist for Future Agents)

1. **One agent per module**, built by a `build_*()` factory that takes its
   dependencies (`model`, `db`, API keys) as arguments.
2. **`role` = one line, `description` = one sentence, `instructions` = details.**
   Keep `description` short — the Team leader reads it to route tasks.
3. **`instructions` accepts a list of strings** — use it to compose persona +
   methodology without string concatenation.
4. **Share one `model` and one `db`** across team members; create them once in a
   config module and inject them.
5. **Custom tools** subclass `agno.tools.Toolkit`, register bound methods in
   `tools=[...]`, and return human-readable strings (agents read them). Keep them in
   a `tools/` package.
6. **Validate env vars lazily** behind a `get_api_key(name)` helper with a clear
   error message — never at module import time.
7. **Structured output** belongs in `output_schema=PydanticModel`, not in unused
   class definitions.
8. **Debug flags** (`debug_mode`, `debug_level`) are configuration — expose them via
   an env toggle (`AGNO_DEBUG`) instead of hardcoding.
9. **Type-check the project** (`basedpyright`): relative imports inside packages,
   beware `list` invariance, suppress library-stub warnings only at the call site.
10. **Document secrets** in `.env.example` and keep `requirements.txt` complete.

---

## 5. Verification

```bash
$ basedpyright 02-TravelPlaning/
0 errors, 0 warnings, 0 notes

$ python -c "import main"
OK — main imports, travel package resolves

# Team construction verified with real keys (no model calls made):
team: travel_planning_team
members: ['travel_planning_agent', 'google_map_agent', 'duckduckgo_agent']
```

Run the app:

```bash
cd 02-TravelPlaning
python main.py
```

Type `exit` or `quit` to stop. Set `AGNO_DEBUG=false` in `.env` to silence team
debug output.
