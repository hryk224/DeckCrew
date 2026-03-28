# DeckCrew

Autonomous AI DJs that debate, adapt, and direct real-time music generation.

[Live Demo](https://hryk224.github.io/DeckCrew/)

## Features

- **AI DJ Meeting** — Three DJ agents (Groove, Harmony, Crowd) propose, debate, and negotiate music direction in real time
- **Lyria Realtime** — Google's music generation API streams live audio that evolves with each turn
- **Critic & Audience** — Virtual evaluators and persona-based listeners react to the set and influence decisions

## Quick Start

![Node.js](https://img.shields.io/badge/Node.js-22%2B-339933?logo=node.js&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![uv](https://img.shields.io/badge/uv-package%20manager-DE5FE9)

```bash
git clone https://github.com/hryk224/DeckCrew.git
cd DeckCrew

cp .env.example .env
# Set GOOGLE_API_KEY in .env (powers both Lyria music and Gemini LLM)

cd frontend && npm install && cd ..
cd backend && uv sync && cd ..

npm run dev:start
# Open http://localhost:3000 → ▶ Play
```

## Environment Variables

Copy `.env.example` to `.env`. The recommended setup needs only one key:

**`GOOGLE_API_KEY`** — powers both Lyria music generation and Gemini LLM for DJ agents.

Without it, the app runs in mock mode (no audio, rule-based agents). See `.env.example` for all options.

## Known Limitations

- **Single-client audio** — The audio WebSocket streams to one browser tab. Multiple tabs split audio chunks.
- **No authentication** — Memory and session APIs have no auth layer. Designed for single-user local use.
- **Mock mode** — Without `GOOGLE_API_KEY`, agents are rule-based and no audio plays.
- **Lyria Realtime** — Experimental API. Connection may drop on idle; the backend auto-reconnects.
