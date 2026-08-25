"""widen persisted user roles

Revision ID: a93d8e71c4b2
Revises: 7b1a4c8e2f90
Create Date: 2026-08-21
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "a93d8e71c4b2"
down_revision: Union[str, Sequence[str], None] = "7b1a4c8e2f90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _alter_role_length(existing_length: int, target_length: int) -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("users") as batch_op:
            batch_op.alter_column(
                "role",
                existing_type=sa.String(length=existing_length),
                type_=sa.String(length=target_length),
                existing_nullable=False,
            )
        return
    op.alter_column(
        "users", "role",
        existing_type=sa.String(length=existing_length),
        type_=sa.String(length=target_length),
        existing_nullable=False,
    )


def upgrade() -> None:
    """Allow every supported RBAC role to be persisted."""
    _alter_role_length(20, 64)


def downgrade() -> None:
    """Shrink only when existing data fits the legacy width."""
    max_length = op.get_bind().execute(sa.text("SELECT MAX(LENGTH(role)) FROM users")).scalar()
    if max_length is not None and int(max_length) > 20:
        raise RuntimeError("Refusing to downgrade: persisted user roles exceed 20 characters")
    _alter_role_length(64, 20)
