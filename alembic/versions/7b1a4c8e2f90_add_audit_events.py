"""add immutable audit event log

Revision ID: 7b1a4c8e2f90
Revises: 50fe141dcef6
Create Date: 2026-08-20
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "7b1a4c8e2f90"
down_revision: Union[str, Sequence[str], None] = "50fe141dcef6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the hash-chained audit log and PostgreSQL immutability guard."""
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("actor_subject", sa.String(length=200), nullable=False),
        sa.Column("actor_username", sa.String(length=200), nullable=False),
        sa.Column("actor_role", sa.String(length=100), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(length=200), nullable=False),
        sa.Column("ministry", sa.String(length=200), nullable=True),
        sa.Column("detail", sa.Text(), nullable=False),
        sa.Column("previous_hash", sa.String(length=64), nullable=False),
        sa.Column("event_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_hash"),
    )
    op.create_index("ix_audit_events_created_at", "audit_events", ["created_at"])
    op.create_index("ix_audit_events_action", "audit_events", ["action"])
    op.create_index("ix_audit_events_actor_subject", "audit_events", ["actor_subject"])

    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            """
            CREATE FUNCTION prevent_audit_event_mutation()
            RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'audit_events is append-only';
            END;
            $$ LANGUAGE plpgsql;
            """
        )
        op.execute(
            """
            CREATE TRIGGER audit_events_immutable
            BEFORE UPDATE OR DELETE ON audit_events
            FOR EACH ROW EXECUTE FUNCTION prevent_audit_event_mutation();
            """
        )
        op.execute(
            """
            CREATE TRIGGER audit_events_no_truncate
            BEFORE TRUNCATE ON audit_events
            FOR EACH STATEMENT EXECUTE FUNCTION prevent_audit_event_mutation();
            """
        )


def downgrade() -> None:
    """Remove an empty audit schema; never destroy recorded security evidence."""
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # Serialize the evidence check and schema removal against concurrent appenders.
        bind.execute(sa.text("LOCK TABLE audit_events IN ACCESS EXCLUSIVE MODE"))
    has_records = bool(
        bind.execute(sa.text("SELECT EXISTS (SELECT 1 FROM audit_events LIMIT 1)")).scalar()
    )
    if has_records:
        raise RuntimeError("Refusing to downgrade: audit_events contains security evidence")
    if bind.dialect.name == "postgresql":
        op.execute("DROP TRIGGER IF EXISTS audit_events_no_truncate ON audit_events")
        op.execute("DROP TRIGGER IF EXISTS audit_events_immutable ON audit_events")
        op.execute("DROP FUNCTION IF EXISTS prevent_audit_event_mutation()")
    op.drop_index("ix_audit_events_actor_subject", table_name="audit_events")
    op.drop_index("ix_audit_events_action", table_name="audit_events")
    op.drop_index("ix_audit_events_created_at", table_name="audit_events")
    op.drop_table("audit_events")
