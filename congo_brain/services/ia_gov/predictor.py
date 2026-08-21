"""GEOS — Predictive SNN Model.

Forecasts SNN evolution over 5-10 years with scenario simulation:
- Investment scenarios (mining, energy, infrastructure)
- Fiscal reform scenarios (tax rate, compliance)
- Anti-corruption scenarios (reduction in DWL)
- Environmental scenarios (EC reduction)

Uses linear regression + Monte Carlo simulation for uncertainty.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class Scenario:
    """A policy scenario with annual changes."""

    name: str
    description: str
    # Annual % changes
    cs_growth: float = 0.0
    ps_growth: float = 0.0
    gr_growth: float = 0.0
    nrv_growth: float = 0.0
    dwl_reduction: float = 0.0  # % reduction per year
    ec_reduction: float = 0.0  # % reduction per year
    # Investment (M USD per year)
    annual_investment: float = 0.0
    investment_snn_multiplier: float = 1.5  # SNN generated per $ invested
    # Monte Carlo
    volatility: float = 0.05  # std dev of annual shocks

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "cs_growth": self.cs_growth,
            "ps_growth": self.ps_growth,
            "gr_growth": self.gr_growth,
            "nrv_growth": self.nrv_growth,
            "dwl_reduction": self.dwl_reduction,
            "ec_reduction": self.ec_reduction,
            "annual_investment": self.annual_investment,
            "investment_snn_multiplier": self.investment_snn_multiplier,
            "volatility": self.volatility,
        }


# ── Preset scenarios ───────────────────────────────────────────

SCENARIOS = {
    "baseline": Scenario(
        name="Baseline (statu quo)",
        description="Pas de changement de politique, tendance actuelle",
        cs_growth=0.02,
        ps_growth=0.015,
        gr_growth=0.025,
        nrv_growth=0.03,
        dwl_reduction=0.01,
        ec_reduction=0.005,
        volatility=0.03,
    ),
    "investissement_minier": Scenario(
        name="Investissement minier massif",
        description="Usines de transformation, augmentation production 30%",
        cs_growth=0.03,
        ps_growth=0.08,
        gr_growth=0.05,
        nrv_growth=0.10,
        dwl_reduction=0.02,
        ec_reduction=-0.02,
        annual_investment=2000,
        investment_snn_multiplier=2.0,
        volatility=0.06,
    ),
    "reforme_fiscale": Scenario(
        name="Réforme fiscale",
        description="Élargissement assiette, réduction évasion, TSCA",
        cs_growth=0.02,
        ps_growth=0.03,
        gr_growth=0.08,
        nrv_growth=0.03,
        dwl_reduction=0.05,
        ec_reduction=0.01,
        volatility=0.04,
    ),
    "anti_corruption": Scenario(
        name="Lutte anti-corruption",
        description="Transparence, e-procurement, audit renforcé",
        cs_growth=0.03,
        ps_growth=0.04,
        gr_growth=0.06,
        nrv_growth=0.03,
        dwl_reduction=0.10,
        ec_reduction=0.02,
        volatility=0.04,
    ),
    "transition_verte": Scenario(
        name="Transition verte",
        description="Énergies renouvelables, réduction EC, tourisme",
        cs_growth=0.04,
        ps_growth=0.02,
        gr_growth=0.03,
        nrv_growth=0.01,
        dwl_reduction=0.03,
        ec_reduction=0.08,
        annual_investment=1500,
        investment_snn_multiplier=1.8,
        volatility=0.05,
    ),
    "optimiste": Scenario(
        name="Scénario optimiste",
        description="Toutes les réformes combinées",
        cs_growth=0.05,
        ps_growth=0.07,
        gr_growth=0.08,
        nrv_growth=0.06,
        dwl_reduction=0.08,
        ec_reduction=0.06,
        annual_investment=3000,
        investment_snn_multiplier=2.2,
        volatility=0.04,
    ),
    "pessimiste": Scenario(
        name="Scénario pessimiste",
        description="Instabilité politique, chute cours matières premières",
        cs_growth=-0.02,
        ps_growth=-0.03,
        gr_growth=-0.01,
        nrv_growth=-0.05,
        dwl_reduction=-0.02,
        ec_reduction=0.01,
        volatility=0.08,
    ),
}


@dataclass
class YearProjection:
    year: int
    cs: float
    ps: float
    gr: float
    nrv: float
    dwl: float
    ec: float
    snn: float
    investment_snn: float = 0.0

    def to_dict(self) -> dict:
        return {
            "year": self.year,
            "cs": round(self.cs, 2),
            "ps": round(self.ps, 2),
            "gr": round(self.gr, 2),
            "nrv": round(self.nrv, 2),
            "dwl": round(self.dwl, 2),
            "ec": round(self.ec, 2),
            "snn": round(self.snn, 2),
            "investment_snn": round(self.investment_snn, 2),
        }


@dataclass
class PredictionResult:
    scenario: str
    horizon_years: int
    base_snn: float
    projections: list[YearProjection]
    final_snn: float
    snn_change: float
    snn_change_pct: float
    # Monte Carlo stats
    mean_final_snn: float = 0.0
    ci_5: float = 0.0
    ci_95: float = 0.0

    def to_dict(self) -> dict:
        return {
            "scenario": self.scenario,
            "horizon_years": self.horizon_years,
            "base_snn": round(self.base_snn, 2),
            "projections": [p.to_dict() for p in self.projections],
            "final_snn": round(self.final_snn, 2),
            "snn_change": round(self.snn_change, 2),
            "snn_change_pct": round(self.snn_change_pct, 1),
            "mean_final_snn": round(self.mean_final_snn, 2),
            "ci_5": round(self.ci_5, 2),
            "ci_95": round(self.ci_95, 2),
        }


class PredictiveModel:
    """Prédictions SNN sur 5-10 ans avec scénarios."""

    def __init__(self) -> None:
        self.base_cs: float = 0.0
        self.base_ps: float = 0.0
        self.base_gr: float = 0.0
        self.base_nrv: float = 0.0
        self.base_dwl: float = 0.0
        self.base_ec: float = 0.0

    def set_baseline(self, cs: float, ps: float, gr: float, nrv: float, dwl: float, ec: float) -> None:
        self.base_cs = cs
        self.base_ps = ps
        self.base_gr = gr
        self.base_nrv = nrv
        self.base_dwl = dwl
        self.base_ec = ec

    def load_from_snn_engine(self, engine) -> None:
        """Load baseline from SNNOptimizationEngine."""
        agg = engine.compute_snn()
        self.base_cs = agg.total_cs
        self.base_ps = agg.total_ps
        self.base_gr = agg.total_gr
        self.base_nrv = agg.total_nrv
        self.base_dwl = agg.total_dwl
        self.base_ec = agg.total_ec

    @property
    def base_snn(self) -> float:
        return self.base_cs + self.base_ps + self.base_gr + self.base_nrv - self.base_dwl - self.base_ec

    def project(self, scenario: Scenario, years: int = 10, monte_carlo_runs: int = 100) -> PredictionResult:
        """Project SNN over `years` under a scenario."""
        # Deterministic projection
        projections = self._deterministic(scenario, years)
        final = projections[-1]

        # Monte Carlo for confidence intervals
        mc_finals = []
        for _ in range(monte_carlo_runs):
            mc_proj = self._stochastic(scenario, years)
            mc_finals.append(mc_proj[-1].snn)
        mc_finals.sort()

        return PredictionResult(
            scenario=scenario.name,
            horizon_years=years,
            base_snn=self.base_snn,
            projections=projections,
            final_snn=final.snn,
            snn_change=final.snn - self.base_snn,
            snn_change_pct=round((final.snn - self.base_snn) / abs(self.base_snn) * 100, 1)
            if self.base_snn != 0
            else 0,
            mean_final_snn=sum(mc_finals) / len(mc_finals),
            ci_5=mc_finals[int(len(mc_finals) * 0.05)],
            ci_95=mc_finals[int(len(mc_finals) * 0.95)],
        )

    def compare_scenarios(self, years: int = 10) -> dict:
        """Compare all preset scenarios."""
        results = {}
        for key, scenario in SCENARIOS.items():
            r = self.project(scenario, years, monte_carlo_runs=50)
            results[key] = {
                "name": scenario.name,
                "description": scenario.description,
                "final_snn": round(r.final_snn, 2),
                "snn_change_pct": r.snn_change_pct,
                "mean_final_snn": round(r.mean_final_snn, 2),
                "ci_5": round(r.ci_5, 2),
                "ci_95": round(r.ci_95, 2),
            }
        return {
            "horizon_years": years,
            "base_snn": round(self.base_snn, 2),
            "scenarios": results,
            "ranking": sorted(
                [
                    {"key": k, "final_snn": v["final_snn"], "change_pct": v["snn_change_pct"]}
                    for k, v in results.items()
                ],
                key=lambda x: x["final_snn"],
                reverse=True,
            ),
        }

    def _deterministic(self, scenario: Scenario, years: int) -> list[YearProjection]:
        cs, ps, gr = self.base_cs, self.base_ps, self.base_gr
        nrv, dwl, ec = self.base_nrv, self.base_dwl, self.base_ec
        projections = []

        for y in range(1, years + 1):
            cs *= 1 + scenario.cs_growth
            ps *= 1 + scenario.ps_growth
            gr *= 1 + scenario.gr_growth
            nrv *= 1 + scenario.nrv_growth
            dwl *= 1 - scenario.dwl_reduction
            ec *= 1 - scenario.ec_reduction

            inv_snn = scenario.annual_investment * scenario.investment_snn_multiplier
            snn = cs + ps + gr + nrv - dwl - ec + inv_snn

            projections.append(
                YearProjection(
                    year=y,
                    cs=cs,
                    ps=ps,
                    gr=gr,
                    nrv=nrv,
                    dwl=dwl,
                    ec=ec,
                    snn=snn,
                    investment_snn=inv_snn,
                )
            )

        return projections

    def _stochastic(self, scenario: Scenario, years: int) -> list[YearProjection]:
        cs, ps, gr = self.base_cs, self.base_ps, self.base_gr
        nrv, dwl, ec = self.base_nrv, self.base_dwl, self.base_ec
        projections = []
        vol = scenario.volatility

        for y in range(1, years + 1):
            shock = random.gauss(0, vol)
            cs *= 1 + scenario.cs_growth + shock
            ps *= 1 + scenario.ps_growth + shock
            gr *= 1 + scenario.gr_growth + shock
            nrv *= 1 + scenario.nrv_growth + shock
            dwl *= 1 - scenario.dwl_reduction + shock * 0.5
            ec *= 1 - scenario.ec_reduction + shock * 0.3

            inv_snn = scenario.annual_investment * scenario.investment_snn_multiplier
            snn = cs + ps + gr + nrv - dwl - ec + inv_snn

            projections.append(
                YearProjection(
                    year=y,
                    cs=cs,
                    ps=ps,
                    gr=gr,
                    nrv=nrv,
                    dwl=dwl,
                    ec=ec,
                    snn=snn,
                    investment_snn=inv_snn,
                )
            )

        return projections

    def get_dashboard(self, years: int = 10) -> dict:
        return {
            "model": "GEOS Predictive",
            "base_snn": round(self.base_snn, 2),
            "horizon_years": years,
            "scenarios_available": list(SCENARIOS.keys()),
            "comparison": self.compare_scenarios(years),
        }
