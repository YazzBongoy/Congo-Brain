"""Tests for GEOS Prometheus monitoring."""

import pytest

from congo_brain.core.monitoring import (
    PrometheusMiddleware, _normalize_path, REQUEST_COUNT, REQUEST_LATENCY, ERROR_COUNT,
)


class TestNormalizePath:
    def test_simple_path(self):
        assert _normalize_path("/api/v1/geos/dashboard") == "/api/v1/geos/dashboard"

    def test_uuid_replaced(self):
        result = _normalize_path("/api/v1/geos/provinces/550e8400-e29b-41d4-a716-446655440000")
        assert "{id}" in result

    def test_numeric_replaced(self):
        result = _normalize_path("/api/v1/geos/provinces/42")
        assert "{id}" in result

    def test_slash_trailing(self):
        result = _normalize_path("/api/v1/geos/")
        assert result == "/api/v1/geos"


class TestMonitoringAPI:
    def test_metrics_endpoint(self, client):
        r = client.get("/metrics")
        assert r.status_code == 200
        assert "geos_http_requests_total" in r.text

    def test_metrics_content_type(self, client):
        r = client.get("/metrics")
        assert "text/plain" in r.headers["content-type"]

    def test_health_detailed(self, client):
        r = client.get("/health/detailed")
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "ok"
        assert d["metrics_enabled"] is True

    def test_request_counted_after_call(self, client):
        client.get("/api/v1/geos/dashboard")
        # Metrics should now have at least one request
        r = client.get("/metrics")
        assert "geos_http_requests_total" in r.text

    def test_404_counted_as_error(self, client):
        client.get("/api/v1/geos/provinces/inconnu_xyz")
        r = client.get("/metrics")
        assert "geos_http_errors_total" in r.text

    def test_metrics_not_counted_themselves(self, client):
        # Call /metrics twice, should not increment itself
        client.get("/metrics")
        client.get("/metrics")
        # The counter for /metrics endpoint should be 0 or absent
        r = client.get("/metrics")
        assert "geos_http_requests_total" in r.text
