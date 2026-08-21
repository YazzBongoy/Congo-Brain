"""Append-only, hash-chained privileged-operation audit events."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, event
from sqlalchemy.orm import Mapped, Mapper, mapped_column

from congo_brain.core.database import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_subject: Mapped[str] = mapped_column(String(200), nullable=False)
    actor_username: Mapped[str] = mapped_column(String(200), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(200), nullable=False)
    ministry: Mapped[str | None] = mapped_column(String(200), nullable=True)
    detail: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


def _reject_mutation(_mapper: Mapper, _connection: object, _target: AuditEvent) -> None:
    raise ValueError("Audit events are immutable")


event.listen(AuditEvent, "before_update", _reject_mutation)
event.listen(AuditEvent, "before_delete", _reject_mutation)
