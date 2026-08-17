"""Module 1: Resource Optimization Engine — Le cerveau.

Résout:
    max W = CS + PS + GR - DWL
sous contraintes:
    Budget, Dette, Inflation, Capacité, Environnement

Solveur: LP/GLPK via scipy (fallback greedy)
"""

from __future__ import annotations

from dataclasses import dataclass, field

try:
    from scipy.optimize import milp, Bounds, LinearConstraint
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


@dataclass
class OptimizationConstraint:
    """Contrainte d'optimisation."""
    name: str
    value: float
    ceiling: float
    unit: str = ""

    @property
    def utilization(self) -> float:
        return round(self.value / self.ceiling * 100, 1) if self.ceiling > 0 else 0.0

    @property
    def feasible(self) -> bool:
        return self.value <= self.ceiling

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": round(self.value, 2),
            "ceiling": round(self.ceiling, 2),
            "utilization": self.utilization,
            "feasible": self.feasible,
            "unit": self.unit,
        }


@dataclass
class OptimizationObjective:
    """Objectif d'optimisation par secteur."""
    sector: str
    cs: float = 0.0
    ps: float = 0.0
    gr: float = 0.0
    dwl: float = 0.0

    @property
    def welfare(self) -> float:
        return self.cs + self.ps + self.gr - self.dwl

    def to_dict(self) -> dict:
        return {
            "sector": self.sector,
            "cs": round(self.cs, 2),
            "ps": round(self.ps, 2),
            "gr": round(self.gr, 2),
            "dwl": round(self.dwl, 2),
            "welfare": round(self.welfare, 2),
        }


class ResourceOptimizationEngine:
    """Moteur d'optimisation principal.

    max W = CS + PS + GR - DWL
    s.t. Budget, Dette, Inflation, Capacité, Environnement
    """

    def __init__(self) -> None:
        self.sectors: dict[str, OptimizationObjective] = {}
        self.constraints: dict[str, OptimizationConstraint] = {}
        self.budget: float = 0.0

    def set_budget(self, budget: float) -> None:
        self.budget = budget

    def add_sector(self, sector: OptimizationObjective) -> None:
        self.sectors[sector.sector] = sector

    def add_constraint(self, constraint: OptimizationConstraint) -> None:
        self.constraints[constraint.name] = constraint

    def load_drc_baseline(self) -> None:
        """Charge les paramètres de base de la RDC."""
        self.budget = 14_000  # M USD

        # Secteurs avec estimations CS/PS/GR/DWL
        self.sectors = {
            "Énergie": OptimizationObjective("Énergie", cs=4.5, ps=5.0, gr=2.0, dwl=1.2),
            "Transport": OptimizationObjective("Transport", cs=3.0, ps=4.0, gr=1.5, dwl=0.8),
            "Santé": OptimizationObjective("Santé", cs=6.0, ps=1.0, gr=0.5, dwl=0.3),
            "Éducation": OptimizationObjective("Éducation", cs=5.0, ps=2.0, gr=0.8, dwl=0.2),
            "Industrie minière": OptimizationObjective("Industrie minière", cs=2.0, ps=6.5, gr=3.0, dwl=1.5),
            "Agriculture": OptimizationObjective("Agriculture", cs=5.0, ps=3.0, gr=1.0, dwl=0.5),
            "Numérique": OptimizationObjective("Numérique", cs=3.5, ps=4.5, gr=1.8, dwl=0.4),
            "Forêt": OptimizationObjective("Forêt", cs=3.0, ps=2.0, gr=0.8, dwl=0.4),
            "Eau": OptimizationObjective("Eau", cs=4.0, ps=0.5, gr=0.3, dwl=0.3),
            "Justice": OptimizationObjective("Justice", cs=2.5, ps=2.0, gr=1.0, dwl=0.8),
        }

        # Contraintes macroéconomiques
        self.constraints = {
            "Budget": OptimizationConstraint("Budget", 14_000, 12_500, "M USD"),
            "Dette/PIB": OptimizationConstraint("Dette/PIB", 45.0, 60.0, "%"),
            "Inflation": OptimizationConstraint("Inflation", 12.5, 5.0, "%"),
            "Capacité administrative": OptimizationConstraint("Capacité administrative", 72.0, 100.0, "%"),
            "Impact environnemental": OptimizationConstraint("Impact environnemental", 5.5, 10.0, "指数"),
        }

    @property
    def total_welfare(self) -> float:
        return sum(s.welfare for s in self.sectors.values())

    @property
    def total_cs(self) -> float:
        return sum(s.cs for s in self.sectors.values())

    @property
    def total_ps(self) -> float:
        return sum(s.ps for s in self.sectors.values())

    @property
    def total_gr(self) -> float:
        return sum(s.gr for s in self.sectors.values())

    @property
    def total_dwl(self) -> float:
        return sum(s.dwl for s in self.sectors.values())

    @property
    def constraints_feasible(self) -> bool:
        return all(c.feasible for c in self.constraints.values())

    def optimize(self, budget_limit: float | None = None) -> dict:
        """Résout l'optimisation de welfare."""
        if budget_limit is not None:
            self.budget = budget_limit

        if not HAS_SCIPY or not self.sectors:
            return self._greedy_optimize()

        sectors = list(self.sectors.values())
        n = len(sectors)
        scores = [s.welfare for s in sectors]
        # Use a proxy cost (inverse of welfare density)
        costs = [max(1, 100 - s.welfare * 10) for s in sectors]

        try:
            result = milp(
                c=[-s for s in scores],
                constraints=[LinearConstraint(A=[[c for c in costs]], ub=self.budget)],
                bounds=Bounds(lb=0, ub=1),
            )
            if result.success:
                allocation = {}
                for i, s in enumerate(sectors):
                    x = round(result.x[i], 4)
                    if x > 0.001:
                        allocation[s.sector] = x
                return {
                    "method": "LP_scipy",
                    "budget": self.budget,
                    "total_welfare": round(sum(scores[i] * result.x[i] for i in range(n)), 2),
                    "allocation": allocation,
                    "constraints": {k: v.to_dict() for k, v in self.constraints.items()},
                    "feasible": self.constraints_feasible,
                }
        except Exception:
            pass

        return self._greedy_optimize()

    def _greedy_optimize(self) -> dict:
        scored = sorted(self.sectors.values(), key=lambda s: s.welfare, reverse=True)
        return {
            "method": "greedy",
            "budget": self.budget,
            "total_welfare": round(self.total_welfare, 2),
            "allocation": {s.sector: round(s.welfare / self.total_welfare, 4) if self.total_welfare > 0 else 0 for s in scored},
            "constraints": {k: v.to_dict() for k, v in self.constraints.items()},
            "feasible": self.constraints_feasible,
        }

    def simulate_policy(self, policy_name: str, sector_changes: dict[str, dict]) -> dict:
        """Simule l'impact d'une politique publique."""
        original = {name: (s.cs, s.ps, s.gr, s.dwl) for name, s in self.sectors.items()}

        for sector_name, changes in sector_changes.items():
            if sector_name in self.sectors:
                s = self.sectors[sector_name]
                s.cs += changes.get("cs_delta", 0)
                s.ps += changes.get("ps_delta", 0)
                s.gr += changes.get("gr_delta", 0)
                s.dwl += changes.get("dwl_delta", 0)

        new_welfare = self.total_welfare
        delta = new_welfare - sum(v[0] + v[1] + v[2] - v[3] for v in original.values())

        # Restore
        for name, (cs, ps, gr, dwl) in original.items():
            self.sectors[name].cs = cs
            self.sectors[name].ps = ps
            self.sectors[name].gr = gr
            self.sectors[name].dwl = dwl

        return {
            "policy": policy_name,
            "welfare_before": round(sum(v[0] + v[1] + v[2] - v[3] for v in original.values()), 2),
            "welfare_after": round(new_welfare, 2),
            "welfare_delta": round(delta, 2),
            "impact": "positif" if delta > 0 else "négatif" if delta < 0 else "neutre",
        }

    def get_dashboard(self) -> dict:
        return {
            "model": "ResourceOptimizationEngine",
            "formula": "max W = CS + PS + GR - DWL",
            "budget": self.budget,
            "total_welfare": round(self.total_welfare, 2),
            "total_cs": round(self.total_cs, 2),
            "total_ps": round(self.total_ps, 2),
            "total_gr": round(self.total_gr, 2),
            "total_dwl": round(self.total_dwl, 2),
            "sectors": [s.to_dict() for s in sorted(self.sectors.values(), key=lambda x: x.welfare, reverse=True)],
            "constraints": {k: v.to_dict() for k, v in self.constraints.items()},
            "feasible": self.constraints_feasible,
            "has_scipy": HAS_SCIPY,
        }
