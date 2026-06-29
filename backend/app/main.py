"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from backend.app.api.v1.panchang import router as panchang_router
from backend.app.config import APP_NAME, APP_VERSION

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/api/v1/health")
def health_check() -> dict[str, str]:
    """Return basic service health."""

    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
    }


app.include_router(panchang_router, prefix="/api/v1")
