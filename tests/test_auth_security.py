"""Security-boundary tests for authentication modes."""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from congo_brain.core import security


def test_keycloak_mode_rejects_locally_signed_token(monkeypatch: pytest.MonkeyPatch) -> None:
    local_token = security.create_access_token({"sub": "local-admin", "role": "admin"})
    monkeypatch.setattr(security, "KEYCLOAK_ENABLED", True)
    monkeypatch.setattr(security, "decode_keycloak_token", lambda _token: None)

    with pytest.raises(HTTPException) as exc:
        security.get_current_user(local_token)

    assert exc.value.status_code == 401


def test_keycloak_mode_accepts_only_normalized_keycloak_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(security, "KEYCLOAK_ENABLED", True)
    monkeypatch.setattr(
        security,
        "decode_keycloak_token",
        lambda _token: {
            "sub": "kc-123",
            "preferred_username": "budget-admin",
            "email": "admin@example.cd",
            "realm_access": {"roles": ["national_budget_admin"]},
        },
    )

    identity = security.get_current_user("keycloak-token")

    assert identity["sub"] == "kc-123"
    assert identity["role"] == "national_budget_admin"
    assert identity["auth_source"] == "keycloak"


def test_keycloak_token_without_application_role_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(security, "KEYCLOAK_ENABLED", True)
    monkeypatch.setattr(
        security,
        "decode_keycloak_token",
        lambda _token: {
            "sub": "kc-ordinary",
            "preferred_username": "ordinary-user",
            "realm_access": {"roles": ["offline_access", "uma_authorization"]},
        },
    )

    with pytest.raises(HTTPException) as exc:
        security.get_current_user("keycloak-token")

    assert exc.value.status_code == 401


@pytest.mark.parametrize("claims", [{}, {"preferred_username": "missing-sub"}, {"sub": ""}])
def test_keycloak_token_without_subject_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    claims: dict,
) -> None:
    monkeypatch.setattr(security, "KEYCLOAK_ENABLED", True)
    monkeypatch.setattr(
        security,
        "decode_keycloak_token",
        lambda _token: {**claims, "realm_access": {"roles": ["executive_viewer"]}},
    )

    with pytest.raises(HTTPException) as exc:
        security.get_current_user("keycloak-token")

    assert exc.value.status_code == 401


@pytest.mark.parametrize(
    "malformed_claims",
    [
        {"realm_access": []},
        {"realm_access": {"roles": ["executive_viewer"]}, "attributes": []},
        {"realm_access": {"roles": ["executive_viewer"]}, "attributes": {"ministry": "Finances"}},
        {"realm_access": {"roles": ["executive_viewer"]}, "preferred_username": ["not-scalar"]},
        {"realm_access": {"roles": ["executive_viewer"]}, "email": {"value": "not-scalar"}},
    ],
)
def test_malformed_keycloak_claim_shapes_are_rejected_with_401(
    monkeypatch: pytest.MonkeyPatch,
    malformed_claims: dict,
) -> None:
    monkeypatch.setattr(security, "KEYCLOAK_ENABLED", True)
    monkeypatch.setattr(
        security,
        "decode_keycloak_token",
        lambda _token: {"sub": "kc-malformed", **malformed_claims},
    )

    with pytest.raises(HTTPException) as exc:
        security.get_current_user("keycloak-token")

    assert exc.value.status_code == 401


def test_local_login_is_disabled_in_keycloak_mode(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from congo_brain.api.v1 import auth

    monkeypatch.setattr(auth, "KEYCLOAK_ENABLED", True, raising=False)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "nobody", "password": "irrelevant"},
    )

    assert response.status_code == 404


def test_public_registration_can_be_disabled(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from congo_brain.api.v1 import auth

    monkeypatch.setattr(auth, "PUBLIC_REGISTRATION_ENABLED", False, raising=False)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "blocked-user",
            "email": "blocked@example.cd",
            "password": "secure-pass",
        },
    )

    assert response.status_code == 404


def test_local_user_management_is_disabled_in_keycloak_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    from congo_brain.api.v1 import auth

    monkeypatch.setattr(auth, "KEYCLOAK_ENABLED", True, raising=False)

    with pytest.raises(HTTPException) as exc:
        auth._ensure_local_user_management()

    assert exc.value.status_code == 404


def test_keycloak_me_uses_normalized_identity_without_local_user() -> None:
    from congo_brain.api.v1 import auth

    identity = auth.get_current_user_info(
        current_user={
            "sub": "kc-123",
            "username": "keycloak-user",
            "email": "keycloak@example.cd",
            "role": "executive_viewer",
            "ministry": None,
            "auth_source": "keycloak",
        },
        db=None,
    )

    assert identity["subject"] == "kc-123"
    assert identity["username"] == "keycloak-user"
    assert identity["auth_source"] == "keycloak"


def test_local_me_rejects_missing_database_session() -> None:
    from congo_brain.api.v1 import auth

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user_info(
            current_user={
                "sub": "local-user",
                "username": "local-user",
                "role": "executive_viewer",
                "auth_source": "local",
            },
            db=None,
        )

    assert exc.value.status_code == 500
    assert exc.value.detail == "Database session unavailable"