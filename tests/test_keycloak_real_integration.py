"""Real Keycloak release gate for role reconciliation and token validation."""

from __future__ import annotations

import os
import subprocess
import uuid
from pathlib import Path
from typing import Any

import pytest
import requests

from congo_brain.core.rbac import Role

KC_URL = os.getenv("KEYCLOAK_TEST_URL")
ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not KC_URL, reason="KEYCLOAK_TEST_URL is not configured")


def _request(method: str, path: str, token: str | None = None, **kwargs: Any) -> requests.Response:
    headers: dict[str, str] = dict(kwargs.pop("headers", {}))
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.request(method, f"{KC_URL}{path}", headers=headers, timeout=10, **kwargs)
    response.raise_for_status()
    return response


def _admin_token() -> str:
    response = _request(
        "POST",
        "/realms/master/protocol/openid-connect/token",
        data={
            "client_id": "admin-cli",
            "username": os.environ.get("KEYCLOAK_ADMIN", "admin"),
            "password": os.environ["KEYCLOAK_ADMIN_PASSWORD"],
            "grant_type": "password",
        },
    )
    return str(response.json()["access_token"])


def _create_user(token: str, username: str, password: str) -> str:
    _request(
        "POST",
        "/admin/realms/congo-brain/users",
        token,
        json={
            "username": username,
            "enabled": True,
            "email": f"{username}@example.invalid",
            "emailVerified": True,
            "firstName": "Workstream",
            "lastName": "Verifier",
            "credentials": [{"type": "password", "value": password, "temporary": False}],
        },
    )
    users = _request(
        "GET", f"/admin/realms/congo-brain/users?username={username}&exact=true", token
    ).json()
    assert len(users) == 1
    return str(users[0]["id"])


def test_real_keycloak_default_role_and_all_application_tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prove the default is minimal and every application role yields a valid JWT."""
    from congo_brain.core import security

    decode_keycloak_token = security.decode_keycloak_token
    monkeypatch.setattr(security, "KEYCLOAK_ENABLED", True)

    token = _admin_token()
    expected_roles = {role.value for role in Role}
    actual_roles = {
        role["name"] for role in _request("GET", "/admin/realms/congo-brain/roles", token).json()
    }
    assert expected_roles <= actual_roles

    created_users: list[str] = []
    client_path = "/admin/realms/congo-brain/clients"
    clients = _request("GET", f"{client_path}?clientId=congo-brain-api", token).json()
    assert len(clients) == 1
    client = clients[0]
    client_uuid = str(client["id"])
    drift_wrapper_name: str | None = None

    try:
        realm = _request("GET", "/admin/realms/congo-brain", token).json()
        default_role_id = str(realm["defaultRole"]["id"])
        admin_role = _request("GET", "/admin/realms/congo-brain/roles/admin", token).json()
        drift_wrapper_name = f"ws2-privileged-wrapper-{uuid.uuid4().hex[:8]}"
        _request("POST", "/admin/realms/congo-brain/roles", token, json={"name": drift_wrapper_name})
        wrapper_role = _request(
            "GET", f"/admin/realms/congo-brain/roles/{drift_wrapper_name}", token
        ).json()
        _request(
            "POST",
            f"/admin/realms/congo-brain/roles-by-id/{wrapper_role['id']}/composites",
            token,
            json=[admin_role],
        )
        _request(
            "POST",
            f"/admin/realms/congo-brain/roles-by-id/{default_role_id}/composites",
            token,
            json=[admin_role, wrapper_role],
        )
        bootstrap_env = os.environ.copy()
        bootstrap_env["KEYCLOAK_URL"] = str(KC_URL)
        bootstrap_env["KEYCLOAK_DIRECT_GRANTS_ENABLED"] = "true"
        bootstrap = subprocess.run(
            ["bash", "scripts/keycloak-init.sh"],
            cwd=ROOT,
            env=bootstrap_env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert bootstrap.returncode == 0, bootstrap.stdout + bootstrap.stderr

        default_username = f"ws2-default-{uuid.uuid4().hex[:10]}"
        default_id = _create_user(token, default_username, "Ws2-default-Only-47!")
        created_users.append(default_id)
        effective = _request(
            "GET", f"/admin/realms/congo-brain/users/{default_id}/role-mappings/realm/composite", token
        ).json()
        effective_application_roles = {role["name"] for role in effective} & expected_roles
        assert effective_application_roles == {Role.PUBLIC_VIEWER.value}

        role_representations = {
            role["name"]: role
            for role in _request("GET", "/admin/realms/congo-brain/roles", token).json()
            if role["name"] in expected_roles
        }
        for role_name in sorted(expected_roles):
            username = f"ws2-{role_name[:12]}-{uuid.uuid4().hex[:8]}"
            password = "Ws2-role-Token-58!"
            user_id = _create_user(token, username, password)
            created_users.append(user_id)
            _request(
                "POST",
                f"/admin/realms/congo-brain/users/{user_id}/role-mappings/realm",
                token,
                json=[role_representations[role_name]],
            )
            access_token = _request(
                "POST",
                "/realms/congo-brain/protocol/openid-connect/token",
                data={
                    "client_id": "congo-brain-api",
                    "client_secret": os.environ["KEYCLOAK_CLIENT_SECRET"],
                    "username": username,
                    "password": password,
                    "grant_type": "password",
                },
            ).json()["access_token"]
            decoded = decode_keycloak_token(access_token)
            assert decoded is not None
            assert role_name in decoded["realm_access"]["roles"]
            monkeypatch.setattr(security, "decode_keycloak_token", lambda _token, payload=decoded: payload)
            normalized = security._try_keycloak(access_token)
            diagnostic = {
                key: decoded.get(key)
                for key in ("sub", "realm_access", "attributes", "ministry", "email", "preferred_username")
            }
            assert normalized is not None, diagnostic
    finally:
        client["directAccessGrantsEnabled"] = False
        _request("PUT", f"{client_path}/{client_uuid}", token, json=client)
        for user_id in created_users:
            _request("DELETE", f"/admin/realms/congo-brain/users/{user_id}", token)
        if drift_wrapper_name is not None:
            _request("DELETE", f"/admin/realms/congo-brain/roles/{drift_wrapper_name}", token)
