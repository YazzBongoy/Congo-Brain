"""MOEG Investment Allocator — LP-based budget allocation with SNN scoring.

Scoring dimensions:
    Maximize: Recettes fiscales, Création d'emplois, Valeur ajoutée locale
    Minimize: Coût du projet, Corruption estimée, Impact environnemental, Temps de réalisation

Net Social Benefit Score:
    NSB = w1*revenue + w2*jobs + w3*nrv + w4*sustainability
          - w5*normalized_cost - w6*corruption - w7*env_impact - w8*duration
"""

from __future__ import annotations

from dataclasses import dataclass

try:
    from scipy.optimize import Bounds, LinearConstraint, milp

    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


@dataclass
class MOEGProject:
    """A public investment project with full MOEG scoring dimensions."""

    name: str
    cost: float  # millions USD — minimize
    # Maximize
    revenue_impact: float = 0.0  # Recettes fiscales générées (0-1)
    jobs_created: int = 0  # Nombre d'emplois créés
    jobs_score: float = 0.0  # Score emploi normalisé (0-1)
    local_value_added: float = 0.0  # Valeur ajoutée locale (0-1)
    # Minimize
    corruption_risk: float = 0.0  # Risque de corruption estimé (0-1)
    env_impact: float = 0.0  # Impact environnemental (0-1)
    duration_months: int = 0  # Temps de réalisation en mois
    # Context
    sector: str = ""
    province: str = ""
    sustainability: float = 0.5  # Soutenabilité globale (0-1)

    @property
    def cost_normalized(self) -> float:
        """Normalized cost (0-1, higher = more expensive)."""
        return min(1.0, self.cost / 5000)  # 5B = max reference

    @property
    def duration_normalized(self) -> float:
        """Normalized duration (0-1, longer = worse)."""
        return min(1.0, self.duration_months / 120)  # 10 years = max

    @property
    def jobs_normalized(self) -> float:
        """Normalized jobs score."""
        return self.jobs_score

    def nsb_score(
        self,
        w_revenue: float = 0.15,
        w_jobs: float = 0.20,
        w_nrv: float = 0.20,
        w_sustainability: float = 0.05,
        w_cost: float = 0.15,
        w_corruption: float = 0.15,
        w_env: float = 0.10,
        w_duration: float = 0.05,
    ) -> float:
        """Net Social Benefit score.

        Positive components (maximize) - Negative components (minimize).
        """
        return (
            w_revenue * self.revenue_impact
            + w_jobs * self.jobs_normalized
            + w_nrv * self.local_value_added
            + w_sustainability * self.sustainability
            - w_cost * self.cost_normalized
            - w_corruption * self.corruption_risk
            - w_env * self.env_impact
            - w_duration * self.duration_normalized
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "cost": self.cost,
            "revenue_impact": self.revenue_impact,
            "jobs_created": self.jobs_created,
            "jobs_score": self.jobs_score,
            "local_value_added": self.local_value_added,
            "corruption_risk": self.corruption_risk,
            "env_impact": self.env_impact,
            "duration_months": self.duration_months,
            "sector": self.sector,
            "province": self.province,
            "sustainability": self.sustainability,
        }


# DRC public investment project candidates (costs in millions USD)
DRC_PROJECT_CANDIDATES: list[dict] = [
    {
        "name": "Autoroute Kinshasa-Lubumbashi",
        "cost": 2500,
        "revenue_impact": 0.7,
        "jobs_created": 50000,
        "jobs_score": 0.9,
        "local_value_added": 0.8,
        "corruption_risk": 0.6,
        "env_impact": 0.5,
        "duration_months": 84,
        "sector": "Transport",
        "province": "Nationale",
        "sustainability": 0.5,
    },
    {
        "name": "Barrage d'Inga III",
        "cost": 5000,
        "revenue_impact": 0.9,
        "jobs_created": 30000,
        "jobs_score": 0.7,
        "local_value_added": 0.9,
        "corruption_risk": 0.7,
        "env_impact": 0.4,
        "duration_months": 96,
        "sector": "Énergie",
        "province": "Kongo Central",
        "sustainability": 0.6,
    },
    {
        "name": "Réseau électrique national",
        "cost": 3000,
        "revenue_impact": 0.8,
        "jobs_created": 40000,
        "jobs_score": 0.8,
        "local_value_added": 0.85,
        "corruption_risk": 0.5,
        "env_impact": 0.3,
        "duration_months": 60,
        "sector": "Énergie",
        "province": "Nationale",
        "sustainability": 0.7,
    },
    {
        "name": "Hôpitaux provinciaux (10)",
        "cost": 800,
        "revenue_impact": 0.3,
        "jobs_created": 15000,
        "jobs_score": 0.6,
        "local_value_added": 0.5,
        "corruption_risk": 0.3,
        "env_impact": 0.1,
        "duration_months": 36,
        "sector": "Santé",
        "province": "Nationale",
        "sustainability": 0.8,
    },
    {
        "name": "Universités techniques (5)",
        "cost": 600,
        "revenue_impact": 0.4,
        "jobs_created": 10000,
        "jobs_score": 0.5,
        "local_value_added": 0.7,
        "corruption_risk": 0.2,
        "env_impact": 0.1,
        "duration_months": 30,
        "sector": "Éducation",
        "province": "Nationale",
        "sustainability": 0.9,
    },
    {
        "name": "Port minéral de Matadi",
        "cost": 1200,
        "revenue_impact": 0.6,
        "jobs_created": 20000,
        "jobs_score": 0.7,
        "local_value_added": 0.6,
        "corruption_risk": 0.5,
        "env_impact": 0.6,
        "duration_months": 48,
        "sector": "Transport",
        "province": "Kongo Central",
        "sustainability": 0.4,
    },
    {
        "name": "Usine de transformation cobalt",
        "cost": 1500,
        "revenue_impact": 0.5,
        "jobs_created": 25000,
        "jobs_score": 0.85,
        "local_value_added": 0.95,
        "corruption_risk": 0.4,
        "env_impact": 0.7,
        "duration_months": 36,
        "sector": "Industrie",
        "province": "Haut-Katanga",
        "sustainability": 0.3,
    },
    {
        "name": "Réseau eau potable (Kinshasa)",
        "cost": 400,
        "revenue_impact": 0.2,
        "jobs_created": 8000,
        "jobs_score": 0.4,
        "local_value_added": 0.4,
        "corruption_risk": 0.4,
        "env_impact": 0.1,
        "duration_months": 24,
        "sector": "Eau",
        "province": "Kinshasa",
        "sustainability": 0.8,
    },
    {
        "name": "Fibre optique nationale",
        "cost": 700,
        "revenue_impact": 0.6,
        "jobs_created": 15000,
        "jobs_score": 0.6,
        "local_value_added": 0.8,
        "corruption_risk": 0.3,
        "env_impact": 0.1,
        "duration_months": 30,
        "sector": "Numérique",
        "province": "Nationale",
        "sustainability": 0.7,
    },
    {
        "name": "Parc solaire Nord-Kivu",
        "cost": 350,
        "revenue_impact": 0.4,
        "jobs_created": 5000,
        "jobs_score": 0.5,
        "local_value_added": 0.5,
        "corruption_risk": 0.3,
        "env_impact": 0.05,
        "duration_months": 18,
        "sector": "Énergie",
        "province": "Nord-Kivu",
        "sustainability": 0.95,
    },
]


class InvestmentAllocator:
    """LP-based investment allocator using Net Social Benefit scoring.

    Solves: max Σ NSB_i * x_i  s.t. Σ cost_i * x_i ≤ Budget
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
        scored = [(p, p.nsb_score(**(weights or {}))) for p in self.projects]
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
        if not HAS_SCIPY or not self.projects:
            return self._greedy_optimize(weights)

        scores = [p.nsb_score(**(weights or {})) for p in self.projects]
        costs = [p.cost for p in self.projects]

        try:
            result = milp(
                c=[-s for s in scores],
                constraints=[LinearConstraint(A=[[c for c in costs]], ub=self.budget)],
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
        results = []
        original = self.budget
        for b in sorted(budgets):
            self.budget = b
            results.append(self.optimize(weights))
        self.budget = original
        return results

    def get_project_scores(self, weights: dict | None = None) -> list[dict]:
        scored = []
        for p in self.projects:
            s = p.nsb_score(**(weights or {}))
            scored.append(
                {
                    **p.to_dict(),
                    "nsb_score": round(s, 4),
                    "cost_effectiveness": round(s / p.cost * 1_000_000, 2) if p.cost > 0 else 0,
                }
            )
        scored.sort(key=lambda x: x["nsb_score"], reverse=True)
        return scored

    def get_dashboard(self) -> dict:
        return {
            "model": "InvestmentAllocator",
            "formula": "NSB = Rev + Emplois + NRV + Sout. - Cout - Corruption - Env - Duree",
            "budget": self.budget,
            "project_count": len(self.projects),
            "has_scipy": HAS_SCIPY,
            "projects": self.get_project_scores(),
        }
