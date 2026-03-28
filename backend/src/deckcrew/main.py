import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deckcrew.api.audio import router as audio_router
from deckcrew.music.registry import music_backend
from deckcrew.api.memory import router as memory_router
from deckcrew.api.session import router as session_router
from deckcrew.api.stream import router as stream_router
from deckcrew.api.turn import router as turn_router

app = FastAPI(title="DeckCrew API")

_cors_origins = os.environ.get(
    "CORS_ORIGINS", "http://localhost:3000,http://localhost:3001"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session_router)
app.include_router(stream_router)
app.include_router(turn_router)
app.include_router(memory_router)
app.include_router(audio_router)

# Debug endpoints: only enabled when DEBUG=1
if os.environ.get("DEBUG", "").strip() in ("1", "true"):
    from deckcrew.api.debug import router as debug_router

    app.include_router(debug_router)


@app.get("/health")
async def health() -> dict[str, object]:
    return {
        "status": "ok",
        "audio_available": music_backend.audio_queue is not None,
    }
