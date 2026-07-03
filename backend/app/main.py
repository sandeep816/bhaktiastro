"""FastAPI application entrypoint."""

from __future__ import annotations

from typing import Dict

from fastapi import FastAPI

from backend.app.api.v1.dasha import router as dasha_router
from backend.app.api.v1.kundali import router as kundali_router
from backend.app.api.v1.panchang import router as panchang_router
from backend.app.config import APP_NAME, APP_VERSION

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/api/v1/health")
def health_check() -> Dict[str, str]:
    """Return basic service health."""

    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
    }


app.include_router(panchang_router, prefix="/api/v1")
app.include_router(kundali_router, prefix="/api/v1")
app.include_router(dasha_router, prefix="/api/v1")
