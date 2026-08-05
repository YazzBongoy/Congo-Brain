"""SQLAlchemy database engine, session, and base model."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from congo_brain.core.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Session:  # type: ignore[misc]
    """Yield a database session for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db  # type: ignore[misc]
    finally:
        db.close()


def init_db() -> None:
    """Create all tables."""
    import congo_brain.models  # noqa: F401 – ensure models are registered
    Base.metadata.create_all(bind=engine)
