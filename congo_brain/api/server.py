"""FastAPI application entry point for Congo-Brain."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from congo_brain import __app_name__, __version__
from congo_brain.api.v1.router import v1_router
from congo_brain.core.config import ENVIRONMENT, KEYCLOAK_ENABLED, KEYCLOAK_JWKS_URL, RATE_LIMIT_PER_MINUTE
from congo_brain.core.database import check_db_health, verify_database_migrations
from congo_brain.core.monitoring import PrometheusMiddleware, metrics_router
from congo_brain.core.rbac import Permission
from congo_brain.core.security import require_permission

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{RATE_LIMIT_PER_MINUTE}/minute"])


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    verify_database_migrations()
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
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(PrometheusMiddleware)

app.include_router(v1_router)
app.include_router(metrics_router)

# GraphQL
try:
    from strawberry.fastapi import GraphQLRouter

    from congo_brain.api.graphql import schema as gql_schema

    graphql_app = GraphQLRouter(
        gql_schema,
        graphql_ide=None if ENVIRONMENT in {"production", "staging"} else "graphiql",
        dependencies=[Depends(require_permission(Permission.NATIONAL_ANALYTICS_READ))],
    )
    app.include_router(graphql_app, prefix="/graphql")
except ImportError:
    pass

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/health", tags=["Health"])
def health_check() -> JSONResponse:
    db_ok = check_db_health()
    keycloak_ok = True
    if KEYCLOAK_ENABLED:
        try:
            import json
            from urllib.request import urlopen

            with urlopen(KEYCLOAK_JWKS_URL, timeout=3) as response:  # noqa: S310 - validated deployment URL
                jwks = json.load(response)
            keycloak_ok = (
                response.status == 200
                and isinstance(jwks, dict)
                and isinstance(jwks.get("keys"), list)
                and bool(jwks["keys"])
            )
        except (OSError, ValueError, TypeError):
            keycloak_ok = False
    status_code = 200 if db_ok and keycloak_ok else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if db_ok and keycloak_ok else "degraded",
            "app": __app_name__,
            "version": __version__,
            "database": "ok" if db_ok else "unreachable",
            "keycloak": "ok" if keycloak_ok else "unreachable",
        },
    )


@app.get("/live", tags=["Health"])
def liveness_check() -> dict[str, str]:
    """Report process liveness without coupling it to external dependencies."""
    return {"status": "alive"}
