# DeckCrew

Autonomous AI DJs that debate, adapt, and direct real-time music generation.

## Directory Structure

```
DeckCrew/
├── frontend/       # Next.js UI
├── backend/        # Python API and agent runtime
│   ├── src/
│   │   └── deckcrew/
│   │       ├── api/            # REST + SSE endpoints
│   │       ├── agent/          # DJ agent definitions and execution
│   │       ├── orchestrator/   # Conductor and turn control
│   │       ├── music/          # Lyria Realtime API integration
│   │       └── state/          # Session state management
│   └── tests/
└── shared/         # Shared contracts and type definitions
```

### frontend/

Next.js application for the user-facing UI.
Displays session state, meeting logs, adopted decisions, and accepts user input.

> Not yet initialized. Will be set up in a subsequent task.

### backend/

Python backend responsible for API endpoints, agent orchestration, music generation control, and session state.

| Package         | Responsibility                                              |
| --------------- | ----------------------------------------------------------- |
| `api/`          | HTTP endpoints (REST for commands, SSE for streaming state) |
| `agent/`        | DJ agent role definitions, prompts, and proposal generation |
| `orchestrator/` | Conductor logic: collect proposals, resolve, emit decisions |
| `music/`        | Lyria Realtime API wrapper with mockable abstraction        |
| `state/`        | In-memory session state: mood, bpm, energy, texture, focus  |

> Package scaffolding is in place (`__init__.py` only). Implementation will follow in subsequent tasks.

### shared/

Candidate location for shared contracts, type definitions, and schemas used across frontend and backend (e.g. SSE event types).

> Currently empty. Contents will be added as cross-boundary contracts emerge.
