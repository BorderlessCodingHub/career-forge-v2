"""Career Forge API — minimal entrypoint (HAC-5 wires routes)."""

from fastapi import FastAPI

app = FastAPI(title="Career Forge API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
