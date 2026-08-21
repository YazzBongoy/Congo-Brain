"""GEOS — Prometheus monitoring middleware + metrics endpoint."""

from __future__ import annotations

import time

from fastapi import APIRouter, Request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# ── Metrics ────────────────────────────────────────────────────

REQUEST_COUNT = Counter(
    "geos_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "geos_http_request_duration_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

SNN_VALUE = Gauge(
    "geos_snn_value",
    "Current Surplus National Net value",
)

ACTIVE_USERS = Gauge(
    "geos_active_users",
    "Number of authenticated requests",
)

ERROR_COUNT = Counter(
    "geos_http_errors_total",
    "Total HTTP error responses (4xx/5xx)",
    ["status", "endpoint"],
)


# ── Middleware ──────────────────────────────────────────────────


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Collects request count, latency, errors."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # Skip metrics endpoint itself
        if path == "/metrics":
            return await call_next(request)

        method = request.method
        start = time.perf_counter()

        response = await call_next(request)

        elapsed = time.perf_counter() - start
        status = str(response.status_code)
        # Normalize path: remove IDs
        endpoint = _normalize_path(path)

        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(elapsed)

        if response.status_code >= 400:
            ERROR_COUNT.labels(status=status, endpoint=endpoint).inc()

        return response


def _normalize_path(path: str) -> str:
    """Replace path params with placeholders."""
    parts = path.strip("/").split("/")
    normalized = []
    for part in parts:
        # Heuristic: if part is UUID or numeric, replace
        if len(part) > 8 and any(c.isdigit() for c in part) and "-" in part:
            normalized.append("{id}")
        elif part.isdigit():
            normalized.append("{id}")
        else:
            normalized.append(part)
    return "/" + "/".join(normalized)


# ── Metrics endpoint ───────────────────────────────────────────

metrics_router = APIRouter(tags=["Monitoring"])


@metrics_router.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@metrics_router.get("/health/detailed")
def health_detailed() -> dict:
    return {
        "status": "ok",
        "metrics_enabled": True,
        "metrics_endpoint": "/metrics",
    }
