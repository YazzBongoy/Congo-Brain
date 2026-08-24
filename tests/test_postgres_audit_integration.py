"""PostgreSQL-only integration tests for audit immutability and concurrency."""

import os
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import sessionmaker

from congo_brain.core import database
from congo_brain.models.audit import AuditEvent
from congo_brain.services.audit_service import record_audit_event, verify_audit_chain

POSTGRES_TEST_URL = os.getenv("POSTGRES_TEST_URL")
pytestmark = pytest.mark.skipif(not POSTGRES_TEST_URL, reason="POSTGRES_TEST_URL is required")


def test_postgresql_audit_chain_is_serialized_and_immutable() -> None:
    assert POSTGRES_TEST_URL is not None
    engine = create_engine(POSTGRES_TEST_URL, pool_pre_ping=True)
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    with session_factory() as session:
        initial_count = session.query(AuditEvent).count()

    def append_event(index: int) -> None:
        with session_factory() as session:
            record_audit_event(
                session,
                {"sub": f"actor-{index}", "username": f"actor-{index}", "role": "admin"},
                "integration.concurrent_append",
                "integration_test",
                index,
                detail={"index": index},
            )

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(append_event, range(16)))

    with session_factory() as session:
        events = session.query(AuditEvent).order_by(AuditEvent.id.asc()).all()
        assert len(events) == initial_count + 16
        assert verify_audit_chain(events) is True
        target_id = events[0].id

        for statement, parameters in (
            ("UPDATE audit_events SET action = 'tampered' WHERE id = :target_id", {"target_id": target_id}),
            ("DELETE FROM audit_events WHERE id = :target_id", {"target_id": target_id}),
            ("TRUNCATE TABLE audit_events", {}),
        ):
            with pytest.raises(DBAPIError):
                session.execute(text(statement), parameters)
                session.commit()
            session.rollback()

        assert session.query(AuditEvent).count() == initial_count + 16
        assert verify_audit_chain(session.query(AuditEvent).order_by(AuditEvent.id.asc()).all()) is True

    engine.dispose()


def test_release_catalog_rejects_disabled_and_replica_only_triggers() -> None:
    """Only origin/always triggers protect normal application writes."""
    assert POSTGRES_TEST_URL is not None
    engine = create_engine(POSTGRES_TEST_URL, pool_pre_ping=True)
    catalog_count = text(
        """
        SELECT COUNT(*)
        FROM pg_trigger t
        JOIN pg_class c ON c.oid = t.tgrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_proc p ON p.oid = t.tgfoid
        WHERE n.nspname = current_schema()
          AND c.relname = 'audit_events'
          AND NOT t.tgisinternal
          AND t.tgenabled IN ('O', 'A')
          AND p.proname = 'prevent_audit_event_mutation'
          AND regexp_replace(p.prosrc, '\\s+', ' ', 'g')
              ~ '^ *BEGIN RAISE EXCEPTION ''audit_events is append-only''; END; *$'
          AND (
            (t.tgname = 'audit_events_immutable' AND t.tgtype = 27)
            OR
            (t.tgname = 'audit_events_no_truncate' AND t.tgtype = 34)
          )
        """
    )

    with engine.begin() as connection:
        try:
            for trigger in ("audit_events_immutable", "audit_events_no_truncate"):
                connection.execute(text(f"ALTER TABLE audit_events ENABLE REPLICA TRIGGER {trigger}"))
            assert connection.execute(catalog_count).scalar_one() == 0

            for trigger in ("audit_events_immutable", "audit_events_no_truncate"):
                connection.execute(text(f"ALTER TABLE audit_events DISABLE TRIGGER {trigger}"))
            assert connection.execute(catalog_count).scalar_one() == 0

            for trigger in ("audit_events_immutable", "audit_events_no_truncate"):
                connection.execute(text(f"ALTER TABLE audit_events ENABLE ALWAYS TRIGGER {trigger}"))
            assert connection.execute(catalog_count).scalar_one() == 2
        finally:
            for trigger in ("audit_events_immutable", "audit_events_no_truncate"):
                connection.execute(text(f"ALTER TABLE audit_events ENABLE TRIGGER {trigger}"))

    engine.dispose()


def test_application_startup_rejects_replica_only_audit_triggers(monkeypatch: pytest.MonkeyPatch) -> None:
    assert POSTGRES_TEST_URL is not None
    engine = create_engine(POSTGRES_TEST_URL, pool_pre_ping=True)
    monkeypatch.setattr(database, "engine", engine)
    try:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE audit_events ENABLE REPLICA TRIGGER audit_events_immutable"))
            connection.execute(text("ALTER TABLE audit_events ENABLE REPLICA TRIGGER audit_events_no_truncate"))
        with pytest.raises(RuntimeError, match="append-only audit triggers"):
            database.verify_database_migrations()
    finally:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE audit_events ENABLE TRIGGER audit_events_immutable"))
            connection.execute(text("ALTER TABLE audit_events ENABLE TRIGGER audit_events_no_truncate"))
        engine.dispose()


def test_application_startup_rejects_permissive_audit_function(monkeypatch: pytest.MonkeyPatch) -> None:
    assert POSTGRES_TEST_URL is not None
    engine = create_engine(POSTGRES_TEST_URL, pool_pre_ping=True)
    monkeypatch.setattr(database, "engine", engine)
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    CREATE OR REPLACE FUNCTION prevent_audit_event_mutation()
                    RETURNS trigger AS $$ BEGIN RETURN COALESCE(NEW, OLD); END; $$ LANGUAGE plpgsql
                    """
                )
            )
        with pytest.raises(RuntimeError, match="append-only audit triggers"):
            database.verify_database_migrations()
    finally:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    CREATE OR REPLACE FUNCTION prevent_audit_event_mutation()
                    RETURNS trigger AS $$
                    BEGIN
                        RAISE EXCEPTION 'audit_events is append-only';
                    END;
                    $$ LANGUAGE plpgsql
                    """
                )
            )
        engine.dispose()
