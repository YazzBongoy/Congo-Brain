"""Identity-provider readiness coverage for the public health endpoint."""

import io
import json
from urllib.error import URLError

import pytest
from fastapi.testclient import TestClient

from congo_brain.api import server


def test_health_fails_closed_when_keycloak_is_unreachable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(server, "KEYCLOAK_ENABLED", True)

    def unreachable(*_args: object, **_kwargs: object) -> None:
        raise URLError("identity provider unavailable")

    monkeypatch.setattr("urllib.request.urlopen", unreachable)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["keycloak"] == "unreachable"


def test_liveness_remains_healthy_during_identity_outage(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(server, "KEYCLOAK_ENABLED", True)

    def unreachable(*_args: object, **_kwargs: object) -> None:
        raise URLError("identity provider unavailable")

    monkeypatch.setattr("urllib.request.urlopen", unreachable)
    response = client.get("/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


@pytest.mark.parametrize("jwks", [[], None, 42, "invalid", {}, {"keys": None}, {"keys": {}}, {"keys": []}])
def test_health_fails_closed_for_malformed_jwks(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, jwks: object
) -> None:
    monkeypatch.setattr(server, "KEYCLOAK_ENABLED", True)

    class FakeResponse(io.BytesIO):
        status = 200

    payload = json.dumps(jwks).encode()
    monkeypatch.setattr("urllib.request.urlopen", lambda *_args, **_kwargs: FakeResponse(payload))

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["keycloak"] == "unreachable"
