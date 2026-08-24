"""Behavioral reconciliation test for the Keycloak bootstrap script."""

from __future__ import annotations

import json
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "keycloak-init.sh"


def test_keycloak_bootstrap_rejects_production_http_before_credentials_or_network() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=ROOT,
        env={
            "PATH": str(Path("/usr/bin")),
            "ENVIRONMENT": "production",
            "KEYCLOAK_SERVER_URL": "http://identity.example.invalid",
        },
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "absolute HTTPS URL" in result.stderr
    assert "KEYCLOAK_ADMIN_PASSWORD is required" not in result.stderr


def test_keycloak_bootstrap_reconciles_insecure_legacy_state() -> None:
    state: dict[str, object] = {
        "realm": {
            "enabled": True,
            "registrationAllowed": True,
            "verifyEmail": False,
        },
        "client": {
            "id": "client-uuid",
            "clientId": "congo-brain-api",
            "enabled": True,
            "publicClient": False,
            "directAccessGrantsEnabled": True,
            "serviceAccountsEnabled": True,
            "standardFlowEnabled": True,
            "implicitFlowEnabled": False,
        },
        "legacy_user": True,
        "default_composites": {"viewer", "admin", "auditor", "privileged-wrapper"},
        "role_closures": {"privileged-wrapper": {"admin"}},
        "audience_mapper": {
            "id": "mapper-uuid",
            "name": "congo-brain-api-audience",
            "protocol": "openid-connect",
            "protocolMapper": "oidc-audience-mapper",
            "config": {"included.client.audience": "wrong-client"},
        },
    }

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            del format, args
            return

        def _body(self) -> dict[str, object]:
            length = int(self.headers.get("Content-Length", "0"))
            if not length:
                return {}
            return json.loads(self.rfile.read(length))

        def _send(self, status: int, body: object | None = None) -> None:
            payload = b"" if body is None else json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_POST(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path.endswith("/protocol/openid-connect/token"):
                self._send(200, {"access_token": "test-token"})
            elif path.endswith("/protocol-mappers/models"):
                mapper = self._body()
                state["audience_mapper"] = {"id": "mapper-uuid", **mapper}
                self._send(201)
            elif path.endswith("/roles-by-id/default-role/composites"):
                composites = state["default_composites"]
                assert isinstance(composites, set)
                composites.add("public_viewer")
                self._send(204)
            elif path == "/admin/realms" or path.endswith("/clients") or path.endswith("/roles"):
                self._send(409, {"error": "exists"})
            else:
                self._send(404)

        def do_PUT(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path == "/admin/realms/congo-brain":
                state["realm"] = {**self._body(), "defaultRole": {"id": "default-role"}}
                self._send(204)
            elif "/protocol-mappers/models/" in path:
                mapper = self._body()
                state["audience_mapper"] = {"id": "mapper-uuid", **mapper}
                self._send(204)
            elif path.endswith("/clients/client-uuid"):
                state["client"] = {"id": "client-uuid", **self._body()}
                self._send(204)
            else:
                self._send(404)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/admin/realms/congo-brain":
                self._send(200, state["realm"])
            elif parsed.path.endswith("/clients/client-uuid/client-secret"):
                client = state["client"]
                assert isinstance(client, dict)
                self._send(200, {"value": client.get("secret")})
            elif parsed.path.endswith("/clients/client-uuid/protocol-mappers/models"):
                self._send(200, [state["audience_mapper"]])
            elif parsed.path.endswith("/clients/client-uuid"):
                self._send(200, state["client"])
            elif parsed.path.endswith("/clients"):
                self._send(200, [state["client"]])
            elif "/roles/" in parsed.path:
                role = parsed.path.rsplit("/", 1)[-1]
                self._send(200, {"id": f"{role}-role", "name": role})
            elif parsed.path.endswith("/roles-by-id/default-role/composites/realm"):
                composites = state["default_composites"]
                closures = state["role_closures"]
                assert isinstance(composites, set) and isinstance(closures, dict)
                effective = set(composites)
                for role in composites:
                    effective.update(closures.get(role, set()))
                self._send(200, [{"id": f"{role}-role", "name": role} for role in sorted(effective)])
            elif "/roles-by-id/" in parsed.path and parsed.path.endswith("/composites/realm"):
                role_id = parsed.path.split("/roles-by-id/", 1)[1].split("/", 1)[0]
                role_name = role_id.removesuffix("-role")
                closures = state["role_closures"]
                assert isinstance(closures, dict)
                self._send(
                    200,
                    [{"id": f"{role}-role", "name": role} for role in sorted(closures.get(role_name, set()))],
                )
            elif parsed.path.endswith("/roles-by-id/public_viewer-role/composites"):
                self._send(200, [])
            elif parsed.path.endswith("/roles-by-id/default-role/composites"):
                composites = state["default_composites"]
                assert isinstance(composites, set)
                self._send(200, [{"id": f"{role}-role", "name": role} for role in sorted(composites)])
            elif parsed.path.endswith("/users"):
                users = [{"id": "legacy-uuid", "username": "admin"}] if state["legacy_user"] else []
                self._send(200, users)
            else:
                self._send(404)

        def do_DELETE(self) -> None:  # noqa: N802
            if "/protocol-mappers/models/" in self.path:
                state["audience_mapper"] = None
                self._send(204)
            elif self.path.endswith("/roles-by-id/public_viewer-role/composites"):
                self._send(204)
            elif self.path.endswith("/roles-by-id/default-role/composites"):
                composites = state["default_composites"]
                assert isinstance(composites, set)
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length))
                assert isinstance(payload, list)
                for role in payload:
                    assert isinstance(role, dict)
                    composites.discard(str(role["name"]))
                self._send(204)
            elif self.path.endswith("/users/legacy-uuid"):
                state["legacy_user"] = False
                self._send(204)
            else:
                self._send(404)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        environment = {
            "PATH": str(Path("/usr/bin")),
            "KEYCLOAK_SERVER_URL": f"http://127.0.0.1:{server.server_port}",
            "KEYCLOAK_ADMIN_PASSWORD": "admin-test-secret",
            "KEYCLOAK_CLIENT_SECRET": "rotated-test-secret",
        }
        refused = subprocess.run(
            ["bash", str(SCRIPT)],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        assert refused.returncode == 3
        assert "CONFIRM_REMOVE_LEGACY_ADMIN=REMOVE" in refused.stderr
        assert state["legacy_user"] is True

        environment["CONFIRM_REMOVE_LEGACY_ADMIN"] = "REMOVE"
        result = subprocess.run(
            ["bash", str(SCRIPT)],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        server.shutdown()
        thread.join(timeout=5)

    assert result.returncode == 0, result.stdout + result.stderr
    realm = state["realm"]
    client = state["client"]
    assert isinstance(realm, dict) and realm["registrationAllowed"] is False and realm["verifyEmail"] is True
    assert isinstance(client, dict) and client["directAccessGrantsEnabled"] is False
    assert client["serviceAccountsEnabled"] is False
    assert client["secret"] == "rotated-test-secret"
    mapper = state["audience_mapper"]
    assert isinstance(mapper, dict)
    assert mapper["config"]["included.client.audience"] == "congo-brain-api"
    assert state["legacy_user"] is False
    assert state["default_composites"] == {"public_viewer"}
