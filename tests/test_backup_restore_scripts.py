"""Fail-closed tests for PostgreSQL backup and restore operator scripts."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKUP_SCRIPT = ROOT / "scripts" / "backup_postgres.sh"
RESTORE_SCRIPT = ROOT / "scripts" / "restore_postgres.sh"


def _tool(directory: Path, name: str, body: str) -> None:
    path = directory / name
    path.write_text(f"#!/usr/bin/env bash\nset -eu\n{body}\n", encoding="utf-8")
    path.chmod(0o755)


def _environment(bin_dir: Path, **values: str) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(values)
    environment["PATH"] = f"{bin_dir}:{environment['PATH']}"
    return environment


def _write_checksum(archive: Path) -> None:
    subprocess.run(
        ["sha256sum", archive.name],
        cwd=archive.parent,
        check=True,
        stdout=archive.with_suffix(".dump.sha256").open("w", encoding="utf-8"),
    )


def test_backup_requires_database_dsn(tmp_path: Path) -> None:
    result = subprocess.run(
        ["bash", str(BACKUP_SCRIPT)],
        cwd=ROOT,
        env=_environment(tmp_path, PG_DSN=""),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "PG_DSN is required" in result.stderr


def test_backup_creates_validated_archive_and_checksum(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    backup_dir = tmp_path / "backups"
    bin_dir.mkdir()
    _tool(
        bin_dir,
        "pg_dump",
        """
for argument in "$@"; do
    case "$argument" in --file=*) output=${argument#--file=} ;; esac
done
printf 'validated archive' > "$output"
""",
    )
    _tool(bin_dir, "pg_restore", "[ \"${1:-}\" = '--list' ]")

    result = subprocess.run(
        ["bash", str(BACKUP_SCRIPT)],
        cwd=ROOT,
        env=_environment(
            bin_dir,
            PG_DSN="postgresql://backup.invalid/congo_brain",
            BACKUP_DIR=str(backup_dir),
        ),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    archives = list(backup_dir.glob("congo_brain-*.dump"))
    assert len(archives) == 1
    assert archives[0].read_text(encoding="utf-8") == "validated archive"
    assert archives[0].with_suffix(".dump.sha256").is_file()


def test_restore_requires_explicit_confirmation(tmp_path: Path) -> None:
    archive = tmp_path / "backup.dump"
    archive.write_text("archive", encoding="utf-8")

    result = subprocess.run(
        ["bash", str(RESTORE_SCRIPT)],
        cwd=ROOT,
        env=_environment(
            tmp_path,
            PG_DSN="postgresql://restore.invalid/congo_brain",
            BACKUP_FILE=str(archive),
        ),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "CONFIRM_RESTORE=RESTORE" in result.stderr


def test_restore_verifies_checksum_and_defaults_to_non_destructive_mode(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    archive = tmp_path / "backup.dump"
    archive.write_text("archive", encoding="utf-8")
    _write_checksum(archive)
    calls = tmp_path / "pg_restore.calls"
    _tool(
        bin_dir,
        "pg_restore",
        f"""
printf '%s\\n' "$*" >> "{calls}"
exit 0
""",
    )
    _tool(bin_dir, "psql", "printf '0\\n'")

    result = subprocess.run(
        ["bash", str(RESTORE_SCRIPT)],
        cwd=ROOT,
        env=_environment(
            bin_dir,
            PG_DSN="postgresql://restore.invalid/congo_brain",
            BACKUP_FILE=str(archive),
            CONFIRM_RESTORE="RESTORE",
        ),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    invocation = calls.read_text(encoding="utf-8")
    assert "--list" in invocation
    assert "--single-transaction" in invocation
    assert "--clean" not in invocation


def test_restore_never_enables_destructive_clean_mode(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    archive = tmp_path / "backup.dump"
    archive.write_text("archive", encoding="utf-8")
    _write_checksum(archive)
    calls = tmp_path / "pg_restore.calls"
    _tool(bin_dir, "pg_restore", f"printf '%s\\n' \"$*\" >> \"{calls}\"")
    _tool(bin_dir, "psql", "printf '0\\n'")

    result = subprocess.run(
        ["bash", str(RESTORE_SCRIPT)],
        cwd=ROOT,
        env=_environment(
            bin_dir,
            PG_DSN="postgresql://restore.invalid/congo_brain",
            BACKUP_FILE=str(archive),
            CONFIRM_RESTORE="RESTORE",
        ),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    invocation = calls.read_text(encoding="utf-8")
    assert "--clean" not in invocation


def test_restore_refuses_non_empty_target(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    archive = tmp_path / "backup.dump"
    archive.write_text("archive", encoding="utf-8")
    _write_checksum(archive)
    _tool(bin_dir, "pg_restore", "exit 0")
    _tool(bin_dir, "psql", "printf '1\\n'")

    result = subprocess.run(
        ["bash", str(RESTORE_SCRIPT)],
        cwd=ROOT,
        env=_environment(
            bin_dir,
            PG_DSN="postgresql://restore.invalid/congo_brain",
            BACKUP_FILE=str(archive),
            CONFIRM_RESTORE="RESTORE",
        ),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "restore target is not empty" in result.stderr


def test_restore_refuses_archive_without_checksum(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _tool(bin_dir, "pg_restore", "exit 0")
    _tool(bin_dir, "psql", "exit 0")
    archive = tmp_path / "backup.dump"
    archive.write_text("archive", encoding="utf-8")

    result = subprocess.run(
        ["bash", str(RESTORE_SCRIPT)],
        cwd=ROOT,
        env=_environment(
            bin_dir,
            PG_DSN="postgresql://restore.invalid/congo_brain",
            BACKUP_FILE=str(archive),
            CONFIRM_RESTORE="RESTORE",
        ),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "checksum sidecar not found" in result.stderr


def test_relative_backup_directory_round_trip_checksum(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _tool(
        bin_dir,
        "pg_dump",
        """
for argument in "$@"; do
    case "$argument" in --file=*) output=${argument#--file=} ;; esac
done
printf 'validated archive' > "$output"
""",
    )
    _tool(bin_dir, "pg_restore", "exit 0")
    _tool(bin_dir, "psql", "printf '0\\n'")

    backup = subprocess.run(
        ["bash", str(BACKUP_SCRIPT)],
        cwd=tmp_path,
        env=_environment(
            bin_dir,
            PG_DSN="postgresql://backup.invalid/congo_brain",
            BACKUP_DIR="./out",
        ),
        capture_output=True,
        text=True,
        check=False,
    )
    assert backup.returncode == 0, backup.stderr
    archive = next((tmp_path / "out").glob("*.dump"))

    restore = subprocess.run(
        ["bash", str(RESTORE_SCRIPT)],
        cwd=tmp_path,
        env=_environment(
            bin_dir,
            PG_DSN="postgresql://restore.invalid/congo_brain",
            BACKUP_FILE=str(archive.relative_to(tmp_path)),
            CONFIRM_RESTORE="RESTORE",
        ),
        capture_output=True,
        text=True,
        check=False,
    )
    assert restore.returncode == 0, restore.stderr


def test_restore_rejects_sidecar_bound_to_another_archive(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _tool(bin_dir, "pg_restore", "exit 0")
    _tool(bin_dir, "psql", "exit 0")
    archive = tmp_path / "selected.dump"
    archive.write_text("selected", encoding="utf-8")
    other = tmp_path / "other.dump"
    other.write_text("other", encoding="utf-8")
    checksum = subprocess.run(
        ["sha256sum", other.name],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    archive.with_suffix(".dump.sha256").write_text(checksum, encoding="utf-8")

    result = subprocess.run(
        ["bash", str(RESTORE_SCRIPT)],
        cwd=ROOT,
        env=_environment(
            bin_dir,
            PG_DSN="postgresql://restore.invalid/congo_brain",
            BACKUP_FILE=str(archive),
            CONFIRM_RESTORE="RESTORE",
        ),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "selected archive basename" in result.stderr
