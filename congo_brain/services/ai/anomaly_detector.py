"""Anomaly detection for budget transactions using statistical methods.

Uses z-score based detection (no sklearn dependency required).
Flags transactions whose amount deviates significantly from the mean.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from congo_brain.models.budget import Transaction


def detect_anomalies(transactions: list[Transaction], threshold: float = 2.0) -> list[Transaction]:
    """Flag anomalous transactions using z-score on amount.

    Args:
        transactions: list of Transaction ORM objects.
        threshold: z-score threshold above which a transaction is flagged.

    Returns:
        list of transactions flagged as anomalies (with is_anomaly and anomaly_score updated).
    """
    if len(transactions) < 3:
        return []

    amounts = [t.amount for t in transactions]
    mean = sum(amounts) / len(amounts)
    variance = sum((a - mean) ** 2 for a in amounts) / len(amounts)
    std = math.sqrt(variance) if variance > 0 else 1.0

    anomalies: list[Transaction] = []
    for t in transactions:
        z = abs(t.amount - mean) / std
        score = min(round(z / (threshold * 2), 2), 1.0)
        if z > threshold:
            t.is_anomaly = True
            t.anomaly_score = score
            anomalies.append(t)
        else:
            t.is_anomaly = False
            t.anomaly_score = score

    return anomalies
