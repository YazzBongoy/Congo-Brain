"""Shared time helpers."""

from datetime import datetime, timezone


def utcnow_naive() -> datetime:
    """Return the current UTC time as a naive ``datetime``.

    ``datetime.utcnow()`` is deprecated (Python 3.12+). The audit chain stores and
    hashes ``created_at`` through a timezone-naive ``DateTime`` column and re-derives
    the hash from the stored value, so the replacement must keep naive-UTC semantics:
    an aware value would append an offset to ``isoformat()`` and break verification of
    every existing row. Dropping ``tzinfo`` after ``now(timezone.utc)`` preserves the
    exact stored representation.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
