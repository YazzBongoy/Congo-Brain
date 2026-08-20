"""PostgreSQL-only integration tests for audit immutability and concurrency."""

import os
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import sessionmaker

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
