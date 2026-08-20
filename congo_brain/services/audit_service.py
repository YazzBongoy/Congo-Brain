"""Audit-log recording and integrity verification."""

import hashlib
import json
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from congo_brain.models.audit import AuditEvent

GENESIS_HASH = "0" * 64
REDACTED = "[REDACTED]"
SENSITIVE_DETAIL_KEYS = {
    "apikey",
    "authorization",
    "clientsecret",
    "credential",
    "credentials",
    "password",
    "passwd",
    "secret",
    "token",
}


def _redact_detail(value: object) -> object:
    """Recursively redact credential-bearing fields before persistence."""
    if isinstance(value, dict):
        sanitized: dict[str, object] = {}
        for key, nested_value in value.items():
            normalized_key = "".join(character for character in str(key).casefold() if character.isalnum())
            sanitized[str(key)] = REDACTED if normalized_key in SENSITIVE_DETAIL_KEYS else _redact_detail(nested_value)
        return sanitized
    if isinstance(value, list):
        return [_redact_detail(item) for item in value]
    if isinstance(value, tuple):
        return [_redact_detail(item) for item in value]
    return value


def _canonical_payload(
    *,
    actor_subject: str,
    actor_username: str,
    actor_role: str,
    action: str,
    resource_type: str,
    resource_id: str,
    ministry: str | None,
    detail: str,
    previous_hash: str,
    created_at: datetime,
) -> str:
    return json.dumps(
        {
            "actor_subject": actor_subject,
            "actor_username": actor_username,
            "actor_role": actor_role,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "ministry": ministry,
            "detail": detail,
            "previous_hash": previous_hash,
            "created_at": created_at.isoformat(),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def record_audit_event(
    db: Session,
    current_user: dict,
    action: str,
    resource_type: str,
    resource_id: str | int,
    *,
    ministry: str | None = None,
    detail: dict | None = None,
) -> AuditEvent:
    """Append and commit one hash-chained audit event."""
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        # Serialize chain appenders so concurrent requests cannot create branches.
        db.execute(text("SELECT pg_advisory_xact_lock(20260820)"))
    previous = db.query(AuditEvent).order_by(AuditEvent.id.desc()).first()
    previous_hash = previous.event_hash if previous else GENESIS_HASH
    created_at = datetime.utcnow()
    detail_json = json.dumps(_redact_detail(detail or {}), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    actor_subject = str(current_user.get("sub", "unknown"))
    actor_username = str(current_user.get("username") or current_user.get("sub") or "unknown")
    actor_role = str(current_user.get("role", "unknown"))
    resource_id_text = str(resource_id)
    payload = _canonical_payload(
        actor_subject=actor_subject,
        actor_username=actor_username,
        actor_role=actor_role,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id_text,
        ministry=ministry,
        detail=detail_json,
        previous_hash=previous_hash,
        created_at=created_at,
    )
    audit_event = AuditEvent(
        actor_subject=actor_subject,
        actor_username=actor_username,
        actor_role=actor_role,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id_text,
        ministry=ministry,
        detail=detail_json,
        previous_hash=previous_hash,
        event_hash=hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        created_at=created_at,
    )
    db.add(audit_event)
    db.commit()
    db.refresh(audit_event)
    return audit_event


def verify_audit_chain(events: list[AuditEvent]) -> bool:
    """Verify event hashes and previous-hash links in ascending order."""
    previous_hash = GENESIS_HASH
    for audit_event in events:
        if audit_event.previous_hash != previous_hash:
            return False
        payload = _canonical_payload(
            actor_subject=audit_event.actor_subject,
            actor_username=audit_event.actor_username,
            actor_role=audit_event.actor_role,
            action=audit_event.action,
            resource_type=audit_event.resource_type,
            resource_id=audit_event.resource_id,
            ministry=audit_event.ministry,
            detail=audit_event.detail,
            previous_hash=audit_event.previous_hash,
            created_at=audit_event.created_at,
        )
        if hashlib.sha256(payload.encode("utf-8")).hexdigest() != audit_event.event_hash:
            return False
        previous_hash = audit_event.event_hash
    return True
