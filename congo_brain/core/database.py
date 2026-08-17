"""SQLAlchemy database engine, session, and base model."""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from congo_brain.core.config import DATABASE_URL, IS_POSTGRES


class Base(DeclarativeBase):
    pass


_connect_args = {"check_same_thread": False} if not IS_POSTGRES else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args,
    pool_pre_ping=True,
    **({"pool_size": 10, "max_overflow": 20} if IS_POSTGRES else {}),
)
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


def check_db_health() -> bool:
    """Verify database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
