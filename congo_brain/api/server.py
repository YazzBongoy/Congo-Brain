"""FastAPI application entry point for Congo-Brain."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from congo_brain import __app_name__, __version__
from congo_brain.api.v1.router import v1_router
from congo_brain.core.database import init_db

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(
    title=__app_name__,
    description=(
        "Congo-Brain — Plateforme IA de gouvernance pour la RDC. "
        "Modules: BudgetGuard, InvestSmart, TranspaFin, PeaceNet, Services Citoyens."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    return {"status": "healthy", "app": __app_name__, "version": __version__}
