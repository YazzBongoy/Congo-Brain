"""Anomaly detection for budget transactions — multi-rule engine.

Combines several detection strategies to flag suspicious transactions:
1. Z-score: statistical outlier by amount (global + per-budget)
2. Over-budget: transaction in a budget where spent exceeds allocation
3. Budget-ratio: single transaction exceeds a large share of the budget
4. Round-number: suspiciously round amounts (potential fabrication)
5. Keyword: description contains known suspicious terms
6. Duplicate: near-identical amounts within the same budget
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from congo_brain.models.budget import Budget, Transaction

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ZSCORE_THRESHOLD = 2.0
BUDGET_RATIO_THRESHOLD = 0.40  # single txn > 40% of budget allocation
ROUND_NUMBER_DIGITS = 11  # amounts with >= 11 trailing zeros are suspicious
DUPLICATE_TOLERANCE = 0.01  # 1% tolerance for near-duplicate amounts

SUSPICIOUS_KEYWORDS = [
    "suspect",
    "secret",
    "confidentiel",
    "anormalement",
    "irregulier",
    "surfactur",
    "fictif",
    "detournement",
    "non justifie",
    "sans justification",
]


# ---------------------------------------------------------------------------
# Individual rule detectors
# ---------------------------------------------------------------------------


def _zscore_flags(transactions: list[Transaction]) -> dict[int, list[str]]:
    """Flag transactions whose amount deviates from the group mean."""
    flags: dict[int, list[str]] = {}
    if len(transactions) < 3:
        return flags

    amounts = [t.amount for t in transactions]
    mean = sum(amounts) / len(amounts)
    variance = sum((a - mean) ** 2 for a in amounts) / len(amounts)
    std = math.sqrt(variance) if variance > 0 else 1.0

    for t in transactions:
        z = abs(t.amount - mean) / std
        if z > ZSCORE_THRESHOLD:
            direction = "superieur" if t.amount > mean else "inferieur"
            flags[t.id] = [
                f"Z-score {z:.1f} ({direction} a la moyenne de {mean:,.0f} FC)"
            ]
    return flags


def _per_budget_zscore(transactions: list[Transaction]) -> dict[int, list[str]]:
    """Z-score analysis within each budget group."""
    flags: dict[int, list[str]] = {}
    by_budget: dict[int, list[Transaction]] = {}
    for t in transactions:
        by_budget.setdefault(t.budget_id, []).append(t)

    for _budget_id, txns in by_budget.items():
        if len(txns) < 3:
            continue
        amounts = [t.amount for t in txns]
        mean = sum(amounts) / len(amounts)
        variance = sum((a - mean) ** 2 for a in amounts) / len(amounts)
        std = math.sqrt(variance) if variance > 0 else 1.0

        for t in txns:
            z = abs(t.amount - mean) / std
            if z > ZSCORE_THRESHOLD:
                flags.setdefault(t.id, []).append(
                    f"Ecart intra-budget (z={z:.1f}, moyenne budget={mean:,.0f} FC)"
                )
    return flags


def _overbudget_flags(
    transactions: list[Transaction],
    budgets: list[Budget],
) -> dict[int, list[str]]:
    """Flag transactions in budgets where total spent exceeds allocated."""
    flags: dict[int, list[str]] = {}
    budget_map = {b.id: b for b in budgets}

    for t in transactions:
        budget = budget_map.get(t.budget_id)
        if not budget:
            continue
        if budget.spent_amount > budget.allocated_amount:
            excess_pct = round(
                (budget.spent_amount - budget.allocated_amount)
                / budget.allocated_amount
                * 100,
                1,
            )
            flags.setdefault(t.id, []).append(
                f"Budget depasse: {budget.ministry} ({excess_pct:+.1f}% au-dela de l'allocation)"
            )
    return flags


def _budget_ratio_flags(
    transactions: list[Transaction],
    budgets: list[Budget],
) -> dict[int, list[str]]:
    """Flag a single transaction that represents too large a share of its budget."""
    flags: dict[int, list[str]] = {}
    budget_map = {b.id: b for b in budgets}

    for t in transactions:
        budget = budget_map.get(t.budget_id)
        if not budget or budget.allocated_amount == 0:
            continue
        ratio = t.amount / budget.allocated_amount
        if ratio > BUDGET_RATIO_THRESHOLD:
            flags.setdefault(t.id, []).append(
                f"Transaction = {ratio * 100:.0f}% du budget alloue ({budget.allocated_amount:,.0f} FC)"
            )
    return flags


def _round_number_flags(transactions: list[Transaction]) -> dict[int, list[str]]:
    """Flag suspiciously round amounts (many trailing zeros)."""
    flags: dict[int, list[str]] = {}
    for t in transactions:
        amt = int(t.amount)
        if amt == 0:
            continue
        trailing = 0
        temp = amt
        while temp % 10 == 0:
            trailing += 1
            temp //= 10
        if trailing >= ROUND_NUMBER_DIGITS:
            flags.setdefault(t.id, []).append(
                f"Montant suspect: {trailing} zeros consecutifs ({t.amount:,.0f} FC)"
            )
    return flags


def _keyword_flags(transactions: list[Transaction]) -> dict[int, list[str]]:
    """Flag transactions whose description contains suspicious keywords."""
    flags: dict[int, list[str]] = {}
    for t in transactions:
        desc_lower = t.description.lower()
        matched = [kw for kw in SUSPICIOUS_KEYWORDS if kw in desc_lower]
        if matched:
            flags.setdefault(t.id, []).append(
                f"Mots-cles suspects dans la description: {', '.join(matched)}"
            )
    return flags


def _duplicate_flags(transactions: list[Transaction]) -> dict[int, list[str]]:
    """Flag near-duplicate amounts within the same budget."""
    flags: dict[int, list[str]] = {}
    by_budget: dict[int, list[Transaction]] = {}
    for t in transactions:
        by_budget.setdefault(t.budget_id, []).append(t)

    for _budget_id, txns in by_budget.items():
        for i, t1 in enumerate(txns):
            for t2 in txns[i + 1 :]:
                if t1.amount == 0:
                    continue
                diff = abs(t1.amount - t2.amount) / max(t1.amount, t2.amount)
                if diff < DUPLICATE_TOLERANCE and t1.id != t2.id:
                    flags.setdefault(t1.id, []).append(
                        f"Montant quasi-identique a {t2.reference_number} ({t2.amount:,.0f} FC)"
                    )
                    flags.setdefault(t2.id, []).append(
                        f"Montant quasi-identique a {t1.reference_number} ({t1.amount:,.0f} FC)"
                    )
    return flags


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def detect_anomalies(
    transactions: list[Transaction],
    budgets: list[Budget] | None = None,
    threshold: float = 2.0,
) -> list[Transaction]:
    """Run all anomaly detection rules and flag suspicious transactions.

    Args:
        transactions: list of Transaction ORM objects.
        budgets: optional list of Budget ORM objects (enables budget-aware rules).
        threshold: z-score threshold (default 2.0).

    Returns:
        list of transactions flagged as anomalies (with is_anomaly, anomaly_score,
        and anomaly_reason updated).
    """
    global ZSCORE_THRESHOLD  # noqa: PLW0603
    ZSCORE_THRESHOLD = threshold

    if not transactions:
        return []

    # Collect flags from all rules
    all_flags: dict[int, list[str]] = {}

    def _merge(new: dict[int, list[str]]) -> None:
        for tid, reasons in new.items():
            all_flags.setdefault(tid, []).extend(reasons)

    _merge(_zscore_flags(transactions))
    _merge(_per_budget_zscore(transactions))
    _merge(_keyword_flags(transactions))
    _merge(_round_number_flags(transactions))
    _merge(_duplicate_flags(transactions))

    if budgets:
        _merge(_overbudget_flags(transactions, budgets))
        _merge(_budget_ratio_flags(transactions, budgets))

    # Score and flag
    max_rules = 7  # total number of rule categories
    anomalies: list[Transaction] = []
    for t in transactions:
        reasons = all_flags.get(t.id, [])
        if reasons:
            t.is_anomaly = True
            t.anomaly_score = min(round(len(reasons) / max_rules, 2), 1.0)
            t.anomaly_reason = " | ".join(reasons)
            anomalies.append(t)
        else:
            t.is_anomaly = False
            t.anomaly_score = 0.0
            t.anomaly_reason = None

    # Sort by score descending
    anomalies.sort(key=lambda x: x.anomaly_score, reverse=True)
    return anomalies
