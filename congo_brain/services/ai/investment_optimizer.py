"""Portfolio optimization using LP/MILP solver.

Selects the best combination of investment projects that maximizes
total composite score (ROI, efficiency, social impact) within a given
budget constraint. Uses scipy.optimize.linprog for linear programming,
with fallback to greedy knapsack if scipy is unavailable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from congo_brain.models.investment import Investment


def _try_lp_optimize(
    investments: list[tuple["Investment", float]],
    budget_limit: float,
) -> dict | None:
    """Attempt LP optimization using scipy.optimize.linprog.

    Each project is a binary variable (0 or 1). We maximize the weighted
    composite score subject to the budget constraint.
    """
    try:
        from scipy.optimize import Bounds, LinearConstraint, milp
    except ImportError:
        return None

    n = len(investments)
    if n == 0:
        return None

    # Costs (remaining budget needed for each project)
    costs = [inv.total_budget - inv.spent_amount for inv, _ in investments]
    # Composite scores (to maximize -> negate for minimization)
    scores = [
        -(inv.roi_score * 0.5 + inv.efficiency_score * 0.3 + inv.social_impact_score * 0.2) for inv, _ in investments
    ]

    # All variables are binary (0 or 1)
    integrality: list[Literal[1]] = [1] * n  # 1 = integer variable

    # Bounds: each variable is 0 or 1
    bounds = Bounds(lb=0, ub=1)

    # Budget constraint: sum(cost_i * x_i) <= budget_limit
    constraint = LinearConstraint(
        A=[costs],
        ub=[budget_limit],
    )

    result = milp(
        c=scores,
        constraints=constraint,
        integrality=integrality,
        bounds=bounds,
    )

    if result.success:
        selected_indices = [i for i, val in enumerate(result.x) if val > 0.5]
        selected = [investments[i][0] for i in selected_indices]
        excluded = [investments[i][0] for i in range(n) if i not in selected_indices]
        total_cost = sum(costs[i] for i in selected_indices)
        total_roi = sum(-scores[i] for i in selected_indices)
        return {
            "selected_projects": selected,
            "projects_excluded": excluded,
            "total_cost": round(total_cost, 2),
            "expected_total_roi": round(total_roi, 1),
            "method": "milp",
        }
    return None


def _greedy_optimize(
    investments: list[tuple["Investment", float]],
    budget_limit: float,
) -> dict:
    """Fallback greedy knapsack optimization."""
    selected = []
    excluded = []
    total_cost = 0.0
    total_roi = 0.0

    for inv, remaining in investments:
        composite = inv.roi_score * 0.5 + inv.efficiency_score * 0.3 + inv.social_impact_score * 0.2
        if total_cost + remaining <= budget_limit:
            selected.append(inv)
            total_cost += remaining
            total_roi += composite
        else:
            excluded.append(inv)

    return {
        "selected_projects": selected,
        "projects_excluded": excluded,
        "total_cost": round(total_cost, 2),
        "expected_total_roi": round(total_roi, 1),
        "method": "greedy",
    }


def optimize_portfolio(investments: list["Investment"], budget_limit: float) -> dict:
    """Optimize investment portfolio using LP/MILP solver with greedy fallback.

    Args:
        investments: candidate Investment ORM objects.
        budget_limit: maximum total budget to spend.

    Returns:
        dict with selected_projects, excluded, total_cost, expected ROI, and method used.
    """
    if not investments:
        return {
            "budget_limit": budget_limit,
            "selected_projects": [],
            "total_cost": 0.0,
            "expected_total_roi": 0.0,
            "projects_excluded": [],
            "method": "none",
        }

    # Prepare investable projects (must have remaining budget)
    scored = []
    for inv in investments:
        remaining = inv.total_budget - inv.spent_amount
        if remaining <= 0:
            continue
        scored.append((inv, remaining))

    # Sort by composite score for greedy fallback
    scored.sort(
        key=lambda x: x[0].roi_score * 0.5 + x[0].efficiency_score * 0.3 + x[0].social_impact_score * 0.2,
        reverse=True,
    )

    # Try LP solver first
    lp_result = _try_lp_optimize(scored, budget_limit)
    if lp_result is not None:
        result = lp_result
    else:
        result = _greedy_optimize(scored, budget_limit)

    result["budget_limit"] = budget_limit
    return result


def compare_scenarios(
    investments: list["Investment"],
    budget_limits: list[float],
) -> list[dict]:
    """Run optimization across multiple budget scenarios for comparison.

    Args:
        investments: candidate Investment ORM objects.
        budget_limits: list of budget amounts to test.

    Returns:
        list of optimization results, one per budget level.
    """
    results = []
    for limit in sorted(budget_limits):
        result = optimize_portfolio(investments, limit)
        results.append(
            {
                "budget_limit": limit,
                "projects_selected": len(result["selected_projects"]),
                "total_cost": result["total_cost"],
                "expected_roi": result["expected_total_roi"],
                "method": result["method"],
            }
        )
    return results
