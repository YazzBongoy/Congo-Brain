"""Shared test fixtures for Congo-Brain.

Test isolation
--------------
The suite used to run against a single repo-relative file (``test_congo_brain.db``)
that every pytest process shared. Two processes — a re-run left running, a CI job, or
two agents working in the same checkout — then issued ``CREATE TABLE`` / ``DROP TABLE``
against the same SQLite file concurrently, producing non-deterministic failures such as
``sqlite3.OperationalError: table X already exists`` and ``no such table: X``.

Each pytest session now gets its own throwaway SQLite file under the system temp
directory. pytest-xdist workers are separate processes, so the ``os.getpid()`` suffix
also isolates them. ``DATABASE_URL`` is set before the application is imported so both
the app engine (``congo_brain.core.database``) and the test engine point at the same
private file. The file (and its temp directory) is deleted at the end of the session.
"""

import os
import shutil
import tempfile
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

_TEST_DB_DIR = tempfile.mkdtemp(prefix="congo_brain_pytest_")
_TEST_DB_PATH = os.path.join(_TEST_DB_DIR, f"test_congo_brain_{os.getpid()}.db")

os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH}"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ENVIRONMENT"] = "development"
os.environ["PUBLIC_REGISTRATION_ENABLED"] = "true"
os.environ["KEYCLOAK_ENABLED"] = "false"

from congo_brain.api.server import app  # noqa: E402
from congo_brain.core.database import Base, get_db  # noqa: E402
from congo_brain.models.user import User  # noqa: E402

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def _isolated_test_database() -> Generator[None, None, None]:
    """Remove the private session database file once the session finishes."""
    yield
    engine.dispose()
    shutil.rmtree(_TEST_DB_DIR, ignore_errors=True)


@pytest.fixture(autouse=True)
def setup_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
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
