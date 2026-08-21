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


def test_production_deployment_manifests_enable_keycloak() -> None:
    helm_values = (ROOT / "helm" / "congo-brain" / "values.yaml").read_text(encoding="utf-8")
    helm_deployment = (ROOT / "helm" / "congo-brain" / "templates" / "deployment-app.yaml").read_text(
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
    assert "- key: KEYCLOAK_ENABLED\n        value: \"true\"" in render_blueprint
