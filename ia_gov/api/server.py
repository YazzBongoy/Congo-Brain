"""FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ia_gov import __app_name__, __version__
from ia_gov.api.routes import router

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(
    title=__app_name__,
    description=(
        "API des services gouvernementaux de la République Démocratique du Congo. "
        "Accédez aux procédures administratives, contacts institutionnels, "
        "droits des citoyens et FAQ."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    """Serve the web interface."""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "app": __app_name__, "version": __version__}
