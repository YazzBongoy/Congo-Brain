"""SQLAlchemy database engine, session, and base model."""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
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
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def verify_database_migrations() -> None:
    """Fail closed unless Alembic is at head and PostgreSQL audit triggers are active."""
    project_root = Path(__file__).resolve().parents[2]
    alembic_config = Config(str(project_root / "alembic.ini"))
    expected_head = ScriptDirectory.from_config(alembic_config).get_current_head()
    try:
        with engine.connect() as conn:
            current_head = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
            if current_head != expected_head:
                raise RuntimeError(f"database migration is {current_head!r}, expected {expected_head!r}")
            if conn.dialect.name == "postgresql":
                trigger_count = conn.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM pg_trigger t
                        JOIN pg_class c ON c.oid = t.tgrelid
                        JOIN pg_namespace n ON n.oid = c.relnamespace
                        JOIN pg_proc p ON p.oid = t.tgfoid
                        JOIN pg_namespace pn ON pn.oid = p.pronamespace
                        JOIN pg_language l ON l.oid = p.prolang
                        WHERE n.nspname = current_schema()
                          AND pn.nspname = current_schema()
                          AND c.relname = 'audit_events'
                          AND NOT t.tgisinternal
                          AND t.tgenabled IN ('O', 'A')
                          AND p.proname = 'prevent_audit_event_mutation'
                          AND l.lanname = 'plpgsql'
                          AND regexp_replace(p.prosrc, '\\s+', ' ', 'g')
                              ~ '^ *BEGIN RAISE EXCEPTION ''audit_events is append-only''; END; *$'
                          AND (
                            (t.tgname = 'audit_events_immutable' AND t.tgtype = 27)
                            OR (t.tgname = 'audit_events_no_truncate' AND t.tgtype = 34)
                          )
                        """
                    )
                ).scalar_one()
                if trigger_count != 2:
                    raise RuntimeError("required append-only audit triggers are not active")
    except SQLAlchemyError as exc:
        raise RuntimeError("database is not Alembic-initialized; run 'alembic upgrade head'") from exc


def check_db_health() -> bool:
    """Verify database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
