"""Fail-closed startup configuration tests."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("environment", ["production", "staging"])
def test_non_development_startup_requires_keycloak(environment: str) -> None:
    process_env = os.environ.copy()
    process_env.update(
        {
            "ENVIRONMENT": environment,
            "SECRET_KEY": "strong-test-only-secret-that-is-not-a-placeholder",
            "KEYCLOAK_ENABLED": "false",
        }
    )

    result = subprocess.run(
        [sys.executable, "-c", "import congo_brain.core.config"],
        check=False,
        capture_output=True,
        text=True,
        env=process_env,
    )

    assert result.returncode != 0
    assert "KEYCLOAK_ENABLED must be true" in result.stderr


@pytest.mark.parametrize("environment", ["production", "staging"])
@pytest.mark.parametrize("keycloak_url", [None, "", "http://identity.example.cd", "not-a-url"])
def test_non_development_startup_requires_explicit_https_keycloak_url(
    environment: str, keycloak_url: str | None
) -> None:
    process_env = os.environ.copy()
    process_env.update(
        {
            "ENVIRONMENT": environment,
            "SECRET_KEY": "strong-test-only-secret-that-is-not-a-placeholder",
            "KEYCLOAK_ENABLED": "true",
        }
    )
    if keycloak_url is None:
        process_env.pop("KEYCLOAK_SERVER_URL", None)
    else:
        process_env["KEYCLOAK_SERVER_URL"] = keycloak_url

    result = subprocess.run(
        [sys.executable, "-c", "import congo_brain.core.config"],
        check=False,
        capture_output=True,
        text=True,
        env=process_env,
    )

    assert result.returncode != 0
    assert "KEYCLOAK_SERVER_URL" in result.stderr


def test_production_accepts_explicit_https_keycloak_url() -> None:
    process_env = os.environ.copy()
    process_env.update(
        {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "strong-test-only-secret-that-is-not-a-placeholder",
            "KEYCLOAK_ENABLED": "true",
            "KEYCLOAK_SERVER_URL": "https://identity.example.cd",
        }
    )
    result = subprocess.run(
        [sys.executable, "-c", "import congo_brain.core.config"],
        check=False,
        capture_output=True,
        text=True,
        env=process_env,
    )
    assert result.returncode == 0, result.stderr


def test_production_deployment_manifests_enable_keycloak() -> None:
    helm_values = (ROOT / "helm" / "congo-brain" / "values.yaml").read_text(encoding="utf-8")
    helm_deployment = (ROOT / "helm" / "congo-brain" / "templates" / "deployment-app.yaml").read_text(
        encoding="utf-8"
    )
    helm_migration = (ROOT / "helm" / "congo-brain" / "templates" / "migration-job.yaml").read_text(
        encoding="utf-8"
    )
    helm_keycloak = (ROOT / "helm" / "congo-brain" / "templates" / "keycloak-init-job.yaml").read_text(
        encoding="utf-8"
    )
    render_blueprint = (ROOT / "render.yaml").read_text(encoding="utf-8")

    assert 'KEYCLOAK_ENABLED: "true"' in helm_values
    assert 'KEYCLOAK_SERVER_URL: ""' in helm_values
    assert 'KEYCLOAK_REALM: "congo-brain"' in helm_values
    assert 'KEYCLOAK_CLIENT_ID: "congo-brain-api"' in helm_values
    for variable in ("KEYCLOAK_SERVER_URL", "KEYCLOAK_REALM", "KEYCLOAK_CLIENT_ID"):
        assert f"- name: {variable}" in helm_deployment
    assert 'required "env.KEYCLOAK_SERVER_URL is required when Keycloak is enabled"' in helm_deployment
    assert "- name: KEYCLOAK_SERVER_URL" in helm_migration
    assert 'required "env.KEYCLOAK_SERVER_URL is required when Keycloak is enabled"' in helm_migration
    assert '"helm.sh/hook-weight": "-10"' in helm_keycloak
    assert "KEYCLOAK_SERVER_URL must be an absolute HTTPS URL" in helm_keycloak
    assert "automountServiceAccountToken: false" in helm_keycloak
    assert "automountServiceAccountToken: false" in helm_migration
    assert 'command: ["bash", "scripts/keycloak-init.sh"]' in helm_keycloak
    assert "identitySecret.existingSecret is required when Keycloak is enabled" in helm_keycloak
    assert "- name: KEYCLOAK_DIRECT_GRANTS_ENABLED\n              value: \"false\"" in helm_keycloak
    assert "- key: KEYCLOAK_ENABLED\n        value: \"true\"" in render_blueprint
    assert "- key: KEYCLOAK_ADMIN_PASSWORD" in render_blueprint
    assert "preDeployCommand: alembic upgrade head && bash scripts/keycloak-init.sh" in render_blueprint
