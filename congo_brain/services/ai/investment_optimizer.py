"""Portfolio optimization using a knapsack-style algorithm.

Selects the best combination of investment projects that maximizes
total ROI within a given budget constraint.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from congo_brain.models.investment import Investment


def optimize_portfolio(investments: list["Investment"], budget_limit: float) -> dict:
    """Optimize investment portfolio using greedy ROI/cost ranking.

    Args:
        investments: candidate Investment ORM objects.
        budget_limit: maximum total budget to spend.

    Returns:
        dict with selected_projects, excluded, total_cost, expected ROI.
    """
    if not investments:
        return {
            "budget_limit": budget_limit,
            "selected_projects": [],
            "total_cost": 0.0,
            "expected_total_roi": 0.0,
            "projects_excluded": [],
        }

    scored = []
    for inv in investments:
        remaining = inv.total_budget - inv.spent_amount
        if remaining <= 0:
            continue
        composite = inv.roi_score * 0.5 + inv.efficiency_score * 0.3 + inv.social_impact_score * 0.2
        ratio = composite / remaining if remaining > 0 else 0
        scored.append((inv, remaining, composite, ratio))

    scored.sort(key=lambda x: x[3], reverse=True)

    selected = []
    excluded = []
    total_cost = 0.0
    total_roi = 0.0

    for inv, remaining, composite, _ in scored:
        if total_cost + remaining <= budget_limit:
            selected.append(inv)
            total_cost += remaining
            total_roi += composite
        else:
            excluded.append(inv)

    return {
        "budget_limit": budget_limit,
        "selected_projects": selected,
        "total_cost": round(total_cost, 2),
        "expected_total_roi": round(total_roi, 1),
        "projects_excluded": excluded,
    }
