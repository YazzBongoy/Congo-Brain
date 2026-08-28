"""Database schema tests for persisted RBAC roles."""

from pathlib import Path

from sqlalchemy import String

from congo_brain.core.rbac import Role
from congo_brain.models.user import User

MIGRATIONS = Path(__file__).resolve().parents[1] / "alembic" / "versions"


def test_user_role_column_fits_every_supported_role() -> None:
    role_type = User.__table__.c.role.type

    assert isinstance(role_type, String)
    assert role_type.length is not None
    assert role_type.length >= max(len(role.value) for role in Role)


def test_alembic_widens_existing_user_role_column() -> None:
    migrations = "\n".join(path.read_text(encoding="utf-8") for path in MIGRATIONS.glob("*.py"))

    assert "op.alter_column(" in migrations
    assert '"users", "role"' in migrations
    assert "sa.String(length=64)" in migrations
