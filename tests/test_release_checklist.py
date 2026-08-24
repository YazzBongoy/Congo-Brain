"""Fail-closed behavior tests for the release checklist."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "release_checklist.sh"


def _tool(directory: Path, name: str, body: str) -> None:
    path = directory / name
    path.write_text(f"#!/usr/bin/env bash\nset -eu\n{body}\n", encoding="utf-8")
    path.chmod(0o755)


def _environment(bin_dir: Path) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{bin_dir}:{environment['PATH']}",
            "BASE_URL": "https://release.invalid",
            "ADMIN_TOKEN": "test-token",
            "PG_DSN": "postgresql://release.invalid/database",
            "KEYCLOAK_MODE": "1",
            "MANUAL_CHECKS_CONFIRMED": "YES",
        }
    )
    return environment


def _common_tools(bin_dir: Path) -> None:
    _tool(
        bin_dir,
        "curl",
        r'''
output=/dev/null
previous=
url=
for argument in "$@"; do
    if [ "$previous" = "-o" ]; then output=$argument; fi
    previous=$argument
    case "$argument" in https://*) url=$argument ;; esac
done
case "$url" in
    */health) code=200 ;;
    */api/v1/auth/login|*/api/v1/auth/register) code=404 ;;
    */api/v1/auth/audit-log*) code=200; printf '{"chain_valid":true}' > "$output" ;;
    */api/v1/geos/provinces) code=401 ;;
    *) code=500 ;;
esac
printf '%s' "$code"
''',
    )
    _tool(bin_dir, "jq", "printf 'true\\n'")


def test_database_failure_cannot_be_reported_as_append_only_success(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _common_tools(bin_dir)
    _tool(bin_dir, "psql", "printf 'connection refused\\n' >&2; exit 2")

    result = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=ROOT,
        env=_environment(bin_dir),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "cannot verify append-only controls" in result.stdout
    assert "append-only audit triggers are present" not in result.stdout


def test_exact_trigger_catalog_passes_even_when_audit_table_is_empty(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _common_tools(bin_dir)
    _tool(
        bin_dir,
        "psql",
        (
            "case \"$*\" in "
            "*\"t.tgenabled IN ('O', 'A')\"*prevent_audit_event_mutation*regexp_replace*append-only*) "
            "printf '2\\n' ;; *) exit 4 ;; esac"
        ),
    )

    result = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=ROOT,
        env=_environment(bin_dir),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "append-only audit triggers are present, enabled and correctly scoped" in result.stdout
