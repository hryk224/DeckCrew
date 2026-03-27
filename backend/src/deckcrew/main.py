from fastapi import FastAPI

from deckcrew.api.session import router as session_router
from deckcrew.api.stream import router as stream_router

app = FastAPI(title="DeckCrew API")
app.include_router(session_router)
app.include_router(stream_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
