"""Fail-closed startup configuration tests."""

import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote_plus

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


def test_docker_compose_requires_external_credentials() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    for variable in (
        "POSTGRES_PASSWORD",
        "KEYCLOAK_ADMIN_PASSWORD",
        "KEYCLOAK_DB_PASSWORD",
        "KEYCLOAK_CLIENT_SECRET",
        "GRAFANA_ADMIN_PASSWORD",
        "SECRET_KEY",
    ):
        assert f"${{{variable}:?" in compose

    for forbidden_literal in (
        "congo_secret_2026",
        "admin_secret_2026",
        "super-secret-key-change-in-production",
        "congo_grafana_2026",
    ):
        assert forbidden_literal not in compose


def test_database_url_components_encode_reserved_password_characters() -> None:
    process_env = os.environ.copy()
    process_env.pop("DATABASE_URL", None)
    process_env.update(
        {
            "DB_HOST": "postgres",
            "DB_PORT": "5432",
            "DB_NAME": "congo_brain",
            "DB_USER": "congo",
            "DB_PASSWORD": "p@ss:word/with#chars",
        }
    )

    result = subprocess.run(
        [sys.executable, "-c", "from congo_brain.core.config import DATABASE_URL; print(DATABASE_URL)"],
        check=True,
        capture_output=True,
        text=True,
        env=process_env,
    )

    assert quote_plus("p@ss:word/with#chars") in result.stdout.strip()


def test_docker_compose_provisions_keycloak_database_and_uses_db_components() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    init_script = (ROOT / "scripts" / "init_keycloak_database.sh").read_text(encoding="utf-8")

    assert "./scripts/init_keycloak_database.sh:/docker-entrypoint-initdb.d/01-create-keycloak-db.sh:ro" in compose
    assert 'DB_PASSWORD: "${POSTGRES_PASSWORD:?Set POSTGRES_PASSWORD}"' in compose
    assert "DATABASE_URL:" not in compose
    assert "CREATE ROLE" in init_script
    assert "CREATE DATABASE" in init_script


def test_release_checklist_exercises_security_controls_with_valid_inputs() -> None:
    checklist = (ROOT / "scripts" / "release_checklist.sh").read_text(encoding="utf-8")

    assert 'Authorization: Bearer $ADMIN_TOKEN' in checklist
    assert "register_payload=$(jq -n" in checklist
    assert "release-check-" in checklist
    assert "registration probe -> ${register}" in checklist
    assert "mktemp" in checklist
    assert "BEGIN; ${stmt}; ROLLBACK;" in checklist
