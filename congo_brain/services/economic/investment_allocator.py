"""MOEG Investment Allocator — LP-based budget allocation.

Solves:
    max  Σ MOEG_score_i * x_i
    s.t. Σ cost_i * x_i ≤ Budget
         0 ≤ x_i ≤ 1   (fraction of project funded)

MOEG_score = w1*CS_impact + w2*PS_impact + w3*jobs_impact + w4*gdp_impact
             - w5*corruption_risk
"""

from __future__ import annotations

from dataclasses import dataclass, field

try:
    from scipy.optimize import milp, Bounds, LinearConstraint
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


@dataclass
class MOEGProject:
    """A public investment project with MOEG scoring dimensions."""
    name: str
    cost: float
    cs_impact: float = 0.0       # Consumer surplus impact (0-1)
    ps_impact: float = 0.0       # Producer surplus impact (0-1)
    jobs_impact: float = 0.0     # Job creation score (0-1)
    gdp_impact: float = 0.0      # GDP growth impact (0-1)
    corruption_risk: float = 0.0 # Corruption risk (0-1, lower is better)
    sector: str = ""
    province: str = ""
    sustainability: float = 0.5  # Environmental/social sustainability (0-1)

    def moeg_score(
        self,
        w_cs: float = 0.25,
        w_ps: float = 0.25,
        w_jobs: float = 0.20,
        w_gdp: float = 0.15,
        w_corruption: float = 0.10,
        w_sustainability: float = 0.05,
    ) -> float:
        """Compute MOEG welfare score for this project."""
        return (
            w_cs * self.cs_impact
            + w_ps * self.ps_impact
            + w_jobs * self.jobs_impact
            + w_gdp * self.gdp_impact
            - w_corruption * self.corruption_risk
            + w_sustainability * self.sustainability
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "cost": self.cost,
            "cs_impact": self.cs_impact,
            "ps_impact": self.ps_impact,
            "jobs_impact": self.jobs_impact,
            "gdp_impact": self.gdp_impact,
            "corruption_risk": self.corruption_risk,
            "sector": self.sector,
            "province": self.province,
            "sustainability": self.sustainability,
        }


# DRC public investment project candidates (costs in millions USD)
DRC_PROJECT_CANDIDATES: list[dict] = [
    {"name": "Autoroute Kinshasa-Lubumbashi", "cost": 2500, "cs_impact": 0.8, "ps_impact": 0.9,
     "jobs_impact": 0.9, "gdp_impact": 0.85, "corruption_risk": 0.6, "sector": "Transport", "province": "Nationale", "sustainability": 0.5},
    {"name": "Barrage d'Inga III", "cost": 5000, "cs_impact": 0.95, "ps_impact": 0.95,
     "jobs_impact": 0.7, "gdp_impact": 0.95, "corruption_risk": 0.7, "sector": "Énergie", "province": "Kongo Central", "sustainability": 0.6},
    {"name": "Réseau électrique national", "cost": 3000, "cs_impact": 0.9, "ps_impact": 0.85,
     "jobs_impact": 0.8, "gdp_impact": 0.9, "corruption_risk": 0.5, "sector": "Énergie", "province": "Nationale", "sustainability": 0.7},
    {"name": "Hôpitaux provinciaux (10)", "cost": 800, "cs_impact": 0.85, "ps_impact": 0.3,
     "jobs_impact": 0.6, "gdp_impact": 0.4, "corruption_risk": 0.3, "sector": "Santé", "province": "Nationale", "sustainability": 0.8},
    {"name": "Universités techniques (5)", "cost": 600, "cs_impact": 0.7, "ps_impact": 0.6,
     "jobs_impact": 0.5, "gdp_impact": 0.7, "corruption_risk": 0.2, "sector": "Éducation", "province": "Nationale", "sustainability": 0.9},
    {"name": "Port minéral de Matadi", "cost": 1200, "cs_impact": 0.5, "ps_impact": 0.9,
     "jobs_impact": 0.7, "gdp_impact": 0.8, "corruption_risk": 0.5, "sector": "Transport", "province": "Kongo Central", "sustainability": 0.4},
    {"name": "Usine de transformation cobalt", "cost": 1500, "cs_impact": 0.3, "ps_impact": 0.95,
     "jobs_impact": 0.85, "gdp_impact": 0.9, "corruption_risk": 0.4, "sector": "Industrie", "province": "Haut-Katanga", "sustainability": 0.3},
    {"name": "Réseau eau potable (Kinshasa)", "cost": 400, "cs_impact": 0.9, "ps_impact": 0.2,
     "jobs_impact": 0.4, "gdp_impact": 0.3, "corruption_risk": 0.4, "sector": "Eau", "province": "Kinshasa", "sustainability": 0.8},
    {"name": "Fibre optique nationale", "cost": 700, "cs_impact": 0.75, "ps_impact": 0.8,
     "jobs_impact": 0.6, "gdp_impact": 0.85, "corruption_risk": 0.3, "sector": "Numérique", "province": "Nationale", "sustainability": 0.7},
    {"name": "Parc solaire Nord-Kivu", "cost": 350, "cs_impact": 0.7, "ps_impact": 0.6,
     "jobs_impact": 0.5, "gdp_impact": 0.5, "corruption_risk": 0.3, "sector": "Énergie", "province": "Nord-Kivu", "sustainability": 0.95},
]


class InvestmentAllocator:
    """LP-based investment allocator using MOEG welfare scores.

    Solves: max Σ score_i * x_i  s.t. Σ cost_i * x_i ≤ Budget
    """

    def __init__(self) -> None:
        self.projects: list[MOEGProject] = []
        self.budget: float = 0.0

    def load_baseline(self) -> None:
        for data in DRC_PROJECT_CANDIDATES:
            self.projects.append(MOEGProject(**data))

    def add_project(self, project: MOEGProject) -> None:
        self.projects.append(project)

    def set_budget(self, budget: float) -> None:
        self.budget = budget

    def _greedy_optimize(self, weights: dict | None = None) -> dict:
        """Greedy fallback when scipy is unavailable."""
        scored = [(p, p.moeg_score(**(weights or {}))) for p in self.projects]
        scored.sort(key=lambda x: x[1], reverse=True)

        allocation = {}
        remaining = self.budget
        total_score = 0.0
        total_cost = 0.0

        for project, score in scored:
            if project.cost <= remaining:
                allocation[project.name] = 1.0
                remaining -= project.cost
                total_score += score
                total_cost += project.cost
            else:
                fraction = remaining / project.cost if project.cost > 0 else 0
                if fraction > 0:
                    allocation[project.name] = round(fraction, 4)
                    total_score += score * fraction
                    total_cost += project.cost * fraction
                    remaining = 0
                break

        return {
            "method": "greedy",
            "budget": self.budget,
            "total_cost": round(total_cost, 2),
            "total_score": round(total_score, 4),
            "remaining": round(remaining, 2),
            "allocation": allocation,
        }

    def optimize(self, weights: dict | None = None) -> dict:
        """Run LP optimization for budget allocation."""
        if not HAS_SCIPY or not self.projects:
            return self._greedy_optimize(weights)

        n = len(self.projects)
        scores = [p.moeg_score(**(weights or {})) for p in self.projects]
        costs = [p.cost for p in self.projects]

        try:
            result = milp(
                c=[-s for s in scores],  # minimize negative = maximize
                constraints=[
                    LinearConstraint(A=[[c for c in costs]], ub=self.budget),
                ],
                bounds=Bounds(lb=0, ub=1),
            )

            if result.success:
                allocation = {}
                total_score = 0.0
                total_cost = 0.0
                for i, p in enumerate(self.projects):
                    x = round(result.x[i], 4)
                    if x > 0.001:
                        allocation[p.name] = x
                        total_score += scores[i] * x
                        total_cost += costs[i] * x

                return {
                    "method": "LP_scipy",
                    "budget": self.budget,
                    "total_cost": round(total_cost, 2),
                    "total_score": round(total_score, 4),
                    "remaining": round(self.budget - total_cost, 2),
                    "allocation": allocation,
                }
        except Exception:
            pass

        return self._greedy_optimize(weights)

    def compare_scenarios(self, budgets: list[float], weights: dict | None = None) -> list[dict]:
        """Run optimization across multiple budget levels."""
        results = []
        original = self.budget
        for b in sorted(budgets):
            self.budget = b
            result = self.optimize(weights)
            results.append(result)
        self.budget = original
        return results

    def get_project_scores(self, weights: dict | None = None) -> list[dict]:
        """Rank all projects by MOEG score."""
        scored = []
        for p in self.projects:
            s = p.moeg_score(**(weights or {}))
            scored.append({
                **p.to_dict(),
                "moeg_score": round(s, 4),
                "cost_effectiveness": round(s / p.cost * 1_000_000, 2) if p.cost > 0 else 0,
            })
        scored.sort(key=lambda x: x["moeg_score"], reverse=True)
        return scored

    def get_dashboard(self) -> dict:
        return {
            "model": "InvestmentAllocator",
            "budget": self.budget,
            "project_count": len(self.projects),
            "has_scipy": HAS_SCIPY,
            "projects": self.get_project_scores(),
        }
