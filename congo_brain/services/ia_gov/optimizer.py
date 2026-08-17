"""IA GOV — Moteur d'Optimisation.

Connecte les résultats de l'IA au modèle SNN:
    Données → Intelligence → Optimisation → (CS, PS, GR) → Décision

Résout:
    max SNN = CS + PS + GR + NRV - DWL - EC
sous contraintes budgétaires et macroéconomiques.
"""

from __future__ import annotations

from dataclasses import dataclass, field

try:
    from scipy.optimize import milp, Bounds, LinearConstraint
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


@dataclass
class GovDecision:
    """A government decision with SNN impact."""
    name: str
    sector: str
    cost: float
    expected_cs: float = 0.0
    expected_ps: float = 0.0
    expected_gr: float = 0.0
    expected_nrv: float = 0.0
    expected_dwl: float = 0.0
    expected_ec: float = 0.0
    duration_months: int = 0
    jobs_created: int = 0

    @property
    def expected_snn(self) -> float:
        return (self.expected_cs + self.expected_ps + self.expected_gr
                + self.expected_nrv - self.expected_dwl - self.expected_ec)

    @property
    def benefit_cost_ratio(self) -> float:
        costs = self.expected_dwl + self.expected_ec + self.cost * 0.01
        return round((self.expected_cs + self.expected_ps + self.expected_gr + self.expected_nrv) / costs, 2) if costs > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "sector": self.sector,
            "cost": round(self.cost, 2),
            "expected_cs": round(self.expected_cs, 2),
            "expected_ps": round(self.expected_ps, 2),
            "expected_gr": round(self.expected_gr, 2),
            "expected_nrv": round(self.expected_nrv, 2),
            "expected_dwl": round(self.expected_dwl, 2),
            "expected_ec": round(self.expected_ec, 2),
            "expected_snn": round(self.expected_snn, 2),
            "benefit_cost_ratio": self.benefit_cost_ratio,
            "duration_months": self.duration_months,
            "jobs_created": self.jobs_created,
        }


@dataclass
class OptimizationResult:
    """Result of government decision optimization."""
    budget: float = 0.0
    total_snn: float = 0.0
    total_cost: float = 0.0
    remaining: float = 0.0
    method: str = ""
    decisions: list[GovDecision] = field(default_factory=list)
    allocation: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "budget": round(self.budget, 2),
            "total_snn": round(self.total_snn, 2),
            "total_cost": round(self.total_cost, 2),
            "remaining": round(self.remaining, 2),
            "method": self.method,
            "decision_count": len(self.decisions),
            "decisions": [d.to_dict() for d in self.decisions],
            "allocation": self.allocation,
        }


class GovOptimizer:
    """Moteur d'optimisation gouvernementale basé sur le SNN.

    Résout:
        max Σ SNN_i * x_i
        s.t. Σ cost_i * x_i ≤ Budget
    """

    def __init__(self) -> None:
        self.decisions: list[GovDecision] = []
        self.budget: float = 0.0

    def load_baseline_decisions(self) -> None:
        """Load typical DRC government investment decisions."""
        self.decisions = [
            GovDecision("Extension réseau électrique", "Énergie", 2000,
                        expected_cs=8.0, expected_ps=6.0, expected_gr=2.0, expected_nrv=0.0,
                        expected_dwl=0.8, expected_ec=0.5, duration_months=48, jobs_created=35000),
            GovDecision("Construction routes nationales", "Transport", 1500,
                        expected_cs=5.0, expected_ps=7.0, expected_gr=1.5, expected_nrv=0.0,
                        expected_dwl=0.9, expected_ec=0.6, duration_months=60, jobs_created=40000),
            GovDecision("Hôpitaux provinciaux", "Santé", 600,
                        expected_cs=7.0, expected_ps=1.0, expected_gr=0.5, expected_nrv=0.0,
                        expected_dwl=0.2, expected_ec=0.1, duration_months=30, jobs_created=12000),
            GovDecision("Usine transformation cobalt", "Industrie minière", 1200,
                        expected_cs=2.0, expected_ps=9.0, expected_gr=3.0, expected_nrv=8.0,
                        expected_dwl=1.0, expected_ec=1.2, duration_months=36, jobs_created=20000),
            GovDecision("Universités techniques", "Éducation", 500,
                        expected_cs=6.0, expected_ps=5.0, expected_gr=1.0, expected_nrv=0.5,
                        expected_dwl=0.2, expected_ec=0.1, duration_months=36, jobs_created=8000),
            GovDecision("Réseau eau potable", "Eau", 350,
                        expected_cs=8.0, expected_ps=0.5, expected_gr=0.3, expected_nrv=0.0,
                        expected_dwl=0.3, expected_ec=0.1, duration_months=24, jobs_created=6000),
            GovDecision("Parcs solaires", "Énergie", 400,
                        expected_cs=5.0, expected_ps=4.0, expected_gr=1.5, expected_nrv=0.0,
                        expected_dwl=0.2, expected_ec=0.05, duration_months=18, jobs_created=5000),
            GovDecision("Fibre optique", "Numérique", 600,
                        expected_cs=6.0, expected_ps=6.0, expected_gr=2.0, expected_nrv=0.0,
                        expected_dwl=0.2, expected_ec=0.1, duration_months=24, jobs_created=10000),
            GovDecision("Foresterie durable", "Forêt", 300,
                        expected_cs=3.0, expected_ps=3.0, expected_gr=1.0, expected_nrv=5.0,
                        expected_dwl=0.3, expected_ec=0.2, duration_months=60, jobs_created=15000),
            GovDecision("Agriculture moderne", "Agriculture", 800,
                        expected_cs=6.0, expected_ps=5.0, expected_gr=1.5, expected_nrv=3.0,
                        expected_dwl=0.3, expected_ec=0.2, duration_months=36, jobs_created=30000),
        ]

    def add_decision(self, decision: GovDecision) -> None:
        self.decisions.append(decision)

    def set_budget(self, budget: float) -> None:
        self.budget = budget

    def _greedy_optimize(self) -> OptimizationResult:
        scored = [(d, d.expected_snn) for d in self.decisions]
        scored.sort(key=lambda x: x[1], reverse=True)

        result = OptimizationResult(budget=self.budget, method="greedy")
        remaining = self.budget

        for decision, snn in scored:
            if decision.cost <= remaining:
                result.decisions.append(decision)
                result.allocation[decision.name] = 1.0
                remaining -= decision.cost
                result.total_snn += snn
                result.total_cost += decision.cost
            else:
                fraction = remaining / decision.cost if decision.cost > 0 else 0
                if fraction > 0:
                    result.allocation[decision.name] = round(fraction, 4)
                    result.total_snn += snn * fraction
                    result.total_cost += decision.cost * fraction
                    remaining = 0
                break

        result.remaining = round(remaining, 2)
        return result

    def optimize(self) -> OptimizationResult:
        if not HAS_SCIPY or not self.decisions:
            return self._greedy_optimize()

        n = len(self.decisions)
        scores = [d.expected_snn for d in self.decisions]
        costs = [d.cost for d in self.decisions]

        try:
            result_milp = milp(
                c=[-s for s in scores],
                constraints=[LinearConstraint(A=[[c for c in costs]], ub=self.budget)],
                bounds=Bounds(lb=0, ub=1),
            )

            if result_milp.success:
                result = OptimizationResult(budget=self.budget, method="LP_scipy")
                for i, d in enumerate(self.decisions):
                    x = round(result_milp.x[i], 4)
                    if x > 0.001:
                        result.decisions.append(d)
                        result.allocation[d.name] = x
                        result.total_snn += scores[i] * x
                        result.total_cost += costs[i] * x
                result.remaining = round(self.budget - result.total_cost, 2)
                return result
        except Exception:
            pass

        return self._greedy_optimize()

    def compare_scenarios(self, budgets: list[float]) -> list[dict]:
        results = []
        original = self.budget
        for b in sorted(budgets):
            self.budget = b
            r = self.optimize()
            results.append(r.to_dict())
        self.budget = original
        return results

    def get_sensitivity_analysis(self) -> list[dict]:
        """Analyze how SNN changes with budget variation."""
        results = []
        for pct in [50, 75, 100, 125, 150]:
            self.budget = self.budget * pct / 100
            r = self.optimize()
            results.append({
                "budget_multiplier": pct / 100,
                "budget": round(self.budget, 2),
                "total_snn": round(r.total_snn, 2),
                "decisions_funded": len(r.decisions),
            })
            self.budget = self.budget * 100 / pct  # restore
        return results

    def get_dashboard(self) -> dict:
        return {
            "model": "GovOptimizer",
            "formula": "max SNN = CS + PS + GR + NRV - DWL - EC",
            "budget": self.budget,
            "decision_count": len(self.decisions),
            "has_scipy": HAS_SCIPY,
        }
