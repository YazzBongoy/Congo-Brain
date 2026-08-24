"""Shared test fixtures for Congo-Brain."""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

TEST_DATABASE_PATH = Path(tempfile.gettempdir()) / f"congo_brain_tests_{os.getpid()}.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DATABASE_PATH}"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ENVIRONMENT"] = "development"
os.environ["PUBLIC_REGISTRATION_ENABLED"] = "true"
os.environ["KEYCLOAK_ENABLED"] = "false"

from congo_brain.api.server import app  # noqa: E402
from congo_brain.core.database import Base, get_db  # noqa: E402
from congo_brain.models.user import User  # noqa: E402

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def pytest_sessionfinish() -> None:
    """Remove the process-isolated SQLite database after the test session."""
    engine.dispose()
    TEST_DATABASE_PATH.unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def setup_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL)"))
        connection.execute(text("DELETE FROM alembic_version"))
        connection.execute(text("INSERT INTO alembic_version (version_num) VALUES ('a93d8e71c4b2')"))
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def _override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client: TestClient, db_session: Session) -> dict:
    """Register a test user and return auth headers."""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "testadmin",
            "email": "admin@test.com",
            "password": "admin123",
        },
    )
    user = db_session.query(User).filter(User.username == "testadmin").one()
    user.role = "admin"
    db_session.commit()
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testadmin",
            "password": "admin123",
        },
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def viewer_headers(client: TestClient) -> dict:
    """Register a viewer user and return auth headers."""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "testviewer",
            "email": "viewer@test.com",
            "password": "viewer123",
        },
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testviewer",
            "password": "viewer123",
        },
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def analyst_headers(client: TestClient, db_session: Session) -> dict:
    """Register an analyst user and return auth headers."""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "testanalyst",
            "email": "analyst@test.com",
            "password": "analyst123",
        },
    )
    user = db_session.query(User).filter(User.username == "testanalyst").one()
    user.role = "analyst"
    db_session.commit()
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testanalyst",
            "password": "analyst123",
        },
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
