from fastapi import FastAPI

from deckcrew.api.session import router as session_router

app = FastAPI(title="DeckCrew API")
app.include_router(session_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
