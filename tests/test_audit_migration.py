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


def test_audit_migration_refuses_to_destroy_existing_security_evidence() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")

    assert "SELECT EXISTS (SELECT 1 FROM audit_events LIMIT 1)" in migration
    assert "Refusing to downgrade: audit_events contains security evidence" in migration


def test_audit_downgrade_serializes_check_and_drop_against_concurrent_inserts() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")
    lock = "LOCK TABLE audit_events IN ACCESS EXCLUSIVE MODE"
    check = "SELECT EXISTS (SELECT 1 FROM audit_events LIMIT 1)"

    assert lock in migration
    assert migration.index(lock) < migration.index(check)
