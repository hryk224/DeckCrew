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
uv run uvicorn deckcrew.main:app --reload --port 8000 --env-file ../.env
```

Stop dev servers (WSL2: `Ctrl+C` may leave child processes):

```bash
# Stop frontend (kills next-server and all child processes)
pkill -f "next-server" 2>/dev/null; pkill -f "next dev" 2>/dev/null

# Stop backend
pkill -f "uvicorn" 2>/dev/null

# Verify ports are free
lsof -i :3000 -t 2>/dev/null && echo "3000 still in use" || echo "3000 free"
lsof -i :8000 -t 2>/dev/null && echo "8000 still in use" || echo "8000 free"
```

Alternatively, use the dev management script:

```bash
npm run dev:start    # Start both servers (PIDs saved to .dev-pids/)
npm run dev:stop     # Stop via saved PIDs
npm run dev:restart  # Stop then start
npm run dev:status   # Show running state
```

### Design Preview

Preview fixed UI states without running the backend:

```bash
npm run dev:start
npm run dev:preview          # List available scenarios
npm run dev:preview build-major  # Print preview URL
# Open the URL in your browser
npm run dev:stop
```

Verify the backend is running:

```bash
curl http://localhost:8000/health
# => {"status":"ok"}
```

## Environment Variables

Defined in `.env.example`. Copy to `.env` before starting.

### Google API Key

A single Google API key powers both music generation (Lyria Realtime) and DJ agent LLM (Gemini). Omit to run in mock mode (no API calls).

| Variable         | Default | Description                         |
| ---------------- | ------- | ----------------------------------- |
| `GOOGLE_API_KEY` | (empty) | Google API key for Lyria and Gemini |

### Music Generation

| Variable        | Default                     | Description                                          |
| --------------- | --------------------------- | ---------------------------------------------------- |
| `MUSIC_BACKEND` | `mock`                      | `mock` for local dev, `lyria` for Lyria Realtime API |
| `LYRIA_MODEL`   | `models/lyria-realtime-exp` | Music generation model                               |

### Agent LLM (advanced override)

By default, `GOOGLE_API_KEY` is used with Gemini for DJ agent LLM. Set these to use a different provider instead.

| Variable         | Default | Description                              |
| ---------------- | ------- | ---------------------------------------- |
| `LLM_API_KEY`    | (empty) | Override API key                         |
| `LLM_BASE_URL`   | (empty) | Override base URL                        |
| `LLM_MODEL_NAME` | (empty) | Override model name (e.g. `gpt-4o-mini`) |

### Server / Frontend

| Variable              | Default                                       | Description                                               |
| --------------------- | --------------------------------------------- | --------------------------------------------------------- |
| `BACKEND_PORT`        | `8000`                                        | Backend server port                                       |
| `CORS_ORIGINS`        | `http://localhost:3000,http://localhost:3001` | Comma-separated allowed origins (override for deployment) |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000`                       | Backend API base URL                                      |

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
