"""Fail-closed application startup tests for mandatory Alembic migrations."""

import pytest
from sqlalchemy import create_engine, text

import congo_brain.models  # noqa: F401
from congo_brain.core import database
from congo_brain.core.database import Base


def test_fresh_database_cannot_start_after_metadata_create_all(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fresh_engine = create_engine(f"sqlite:///{tmp_path / 'fresh.db'}")
    Base.metadata.create_all(bind=fresh_engine)
    monkeypatch.setattr(database, "engine", fresh_engine)

    with pytest.raises(RuntimeError, match="Alembic-initialized"):
        database.verify_database_migrations()


def test_stale_alembic_revision_cannot_start(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    stale_engine = create_engine(f"sqlite:///{tmp_path / 'stale.db'}")
    with stale_engine.begin() as connection:
        connection.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
        connection.execute(text("INSERT INTO alembic_version VALUES ('50fe141dcef6')"))
    monkeypatch.setattr(database, "engine", stale_engine)

    with pytest.raises(RuntimeError, match="expected"):
        database.verify_database_migrations()
