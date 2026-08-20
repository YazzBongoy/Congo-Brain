"""Security assertions for the audit-log Alembic migration."""

from pathlib import Path

MIGRATION = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "7b1a4c8e2f90_add_audit_events.py"
)


def test_postgresql_audit_migration_blocks_row_mutation_and_truncate() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")

    assert "BEFORE UPDATE OR DELETE" in migration
    assert "BEFORE TRUNCATE" in migration
    assert "FOR EACH STATEMENT" in migration
