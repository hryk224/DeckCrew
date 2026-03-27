# DeckCrew

Autonomous AI DJs that debate, adapt, and direct real-time music generation.

## Prerequisites

- [Node.js](https://nodejs.org/) v22+
- [Python](https://www.python.org/) 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

## Setup

```bash
# Clone the repository
git clone https://github.com/hryk224/DeckCrew.git
cd DeckCrew

# Copy environment variables
cp .env.example .env
# Edit .env as needed (see Environment Variables below)

# Install frontend dependencies
cd frontend
npm install
cd ..

# Install backend dependencies
cd backend
uv sync --extra dev
cd ..
```

## Development

Start each service in a separate terminal:

```bash
# Terminal 1: Frontend (http://localhost:3000)
cd frontend
npm run dev

# Terminal 2: Backend (http://localhost:8000)
cd backend
uv run uvicorn deckcrew.main:app --reload --port 8000
```

Verify the backend is running:

```bash
curl http://localhost:8000/health
# => {"status":"ok"}
```

## Environment Variables

Defined in `.env.example`. Copy to `.env` before starting.

| Variable              | Default                 | Description                                          |
| --------------------- | ----------------------- | ---------------------------------------------------- |
| `MUSIC_BACKEND`       | `mock`                  | `mock` for local dev, `lyria` for Lyria Realtime API |
| `LYRIA_API_KEY`       | (empty)                 | Required only when `MUSIC_BACKEND=lyria`             |
| `LLM_MODEL`           | (empty)                 | LLM model identifier for agent calls                 |
| `BACKEND_PORT`        | `8000`                  | Backend server port                                  |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API base URL used by frontend                |

## Configuration Files

| File                     | Purpose                                            |
| ------------------------ | -------------------------------------------------- |
| `.npmrc`                 | npm security settings (save-exact, ignore-scripts) |
| `.env.example`           | Environment variable template                      |
| `frontend/package.json`  | Frontend dependencies and scripts                  |
| `backend/pyproject.toml` | Backend dependencies and tool configuration        |

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

### backend/

Python backend responsible for API endpoints, agent orchestration, music generation control, and session state.

| Package         | Responsibility                                              |
| --------------- | ----------------------------------------------------------- |
| `api/`          | HTTP endpoints (REST for commands, SSE for streaming state) |
| `agent/`        | DJ agent role definitions, prompts, and proposal generation |
| `orchestrator/` | Conductor logic: collect proposals, resolve, emit decisions |
| `music/`        | Lyria Realtime API wrapper with mockable abstraction        |
| `state/`        | In-memory session state: mood, bpm, energy, texture, focus  |

### shared/

Candidate location for shared contracts, type definitions, and schemas used across frontend and backend (e.g. SSE event types).

> Currently empty. Contents will be added as cross-boundary contracts emerge.
