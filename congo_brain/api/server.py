"""FastAPI application entry point for Congo-Brain."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from congo_brain import __app_name__, __version__
from congo_brain.api.v1.router import v1_router
from congo_brain.core.config import RATE_LIMIT_PER_MINUTE
from congo_brain.core.database import check_db_health, init_db

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{RATE_LIMIT_PER_MINUTE}/minute"])


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

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
def health_check() -> JSONResponse:
    db_ok = check_db_health()
    status_code = 200 if db_ok else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if db_ok else "degraded",
            "app": __app_name__,
            "version": __version__,
            "database": "ok" if db_ok else "unreachable",
        },
    )
