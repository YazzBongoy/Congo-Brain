"""IA GOV — Tableau de bord et Décision Gouvernementale.

Assemble les résultats de:
    Collecte → Intelligence → Optimisation → Dashboard → Décision
"""

from __future__ import annotations

from typing import cast

from congo_brain.services.ia_gov.collectors import DataCollector
from congo_brain.services.ia_gov.intelligence import IntelligenceEngine
from congo_brain.services.ia_gov.optimizer import GovOptimizer


class GovDashboard:
    """Tableau de bord intégré IA GOV.

    Pipeline: Collecte → Intelligence → Optimisation → Décision
    """

    def __init__(self) -> None:
        self.collector = DataCollector()
        self.engine = IntelligenceEngine()
        self.optimizer = GovOptimizer()

    def run_full_analysis(self, budget: float = 10_000) -> dict:
        """Exécute le pipeline complet IA GOV."""
        self.collector.load_drc_baseline()
        all_data = self.collector.get_all()

        analysis = self.engine.analyze(
            budget_data=all_data["budget"],
            economic_data=all_data["economy"],
            social_data=all_data["social"],
        )

        self.optimizer.load_baseline_decisions()
        self.optimizer.set_budget(budget)
        optimization = self.optimizer.optimize()

        return {
            "pipeline": "Collecte → Intelligence → Optimisation → Décision",
            "data": all_data,
            "analysis": analysis.to_dict(),
            "optimization": optimization.to_dict(),
            "summary": self._build_summary(analysis, optimization),
        }

    def get_welfare_status(self) -> dict:
        """Quick welfare status overview."""
        self.collector.load_drc_baseline()
        all_data = self.collector.get_all()

        analysis = self.engine.analyze(
            budget_data=all_data["budget"],
            economic_data=all_data["economy"],
            social_data=all_data["social"],
        )

        total_benefit = sum(
            s.consumer_surplus + s.producer_surplus + s.government_revenue + s.natural_resource_value
            for s in analysis.sector_surpluses
        )
        total_cost = sum(s.deadweight_loss + s.environmental_cost for s in analysis.sector_surpluses)

        return {
            "national_snn": round(analysis.national_snn, 2),
            "total_benefit": round(total_benefit, 2),
            "total_cost": round(total_cost, 2),
            "efficiency": round(analysis.national_snn / total_benefit * 100, 1) if total_benefit > 0 else 0,
            "alerts_count": len(analysis.alerts),
            "critical_alerts": len([a for a in analysis.alerts if a["level"] == "critique"]),
            "recommendations_count": len(analysis.recommendations),
        }

    def get_sector_analysis(self) -> list[dict]:
        """Detailed sector-level surplus analysis."""
        self.collector.load_drc_baseline()
        all_data = self.collector.get_all()

        analysis = self.engine.analyze(
            budget_data=all_data["budget"],
            economic_data=all_data["economy"],
            social_data=all_data["social"],
        )

        return [s.to_dict() for s in analysis.sector_surpluses]

    def get_decision_support(self, budget: float = 10_000) -> dict:
        """Decision support with optimization and scenarios."""
        self.optimizer.load_baseline_decisions()
        self.optimizer.set_budget(budget)

        optimization = self.optimizer.optimize()
        scenarios = self.optimizer.compare_scenarios([5000, 10000, 15000, 20000])
        sensitivity = self.optimizer.get_sensitivity_analysis()

        return {
            "optimal_allocation": optimization.to_dict(),
            "scenarios": scenarios,
            "sensitivity": sensitivity,
        }

    def get_alerts(self) -> list[dict]:
        """Get current governance alerts."""
        self.collector.load_drc_baseline()
        all_data = self.collector.get_all()

        analysis = self.engine.analyze(
            budget_data=all_data["budget"],
            economic_data=all_data["economy"],
            social_data=all_data["social"],
        )

        return cast(list[dict], analysis.alerts)

    def get_recommendations(self) -> list[dict]:
        """Get optimization recommendations."""
        self.collector.load_drc_baseline()
        all_data = self.collector.get_all()

        analysis = self.engine.analyze(
            budget_data=all_data["budget"],
            economic_data=all_data["economy"],
            social_data=all_data["social"],
        )

        return cast(list[dict], analysis.recommendations)

    def get_historical(self, years: int = 5) -> list[dict]:
        """Get historical trends."""
        return self.collector.get_historical(years)

    def _build_summary(self, analysis, optimization) -> dict:
        return {
            "national_snn": round(analysis.national_snn, 2),
            "funded_decisions": len(optimization.decisions),
            "total_investment": round(optimization.total_cost, 2),
            "snn_per_dollar": round(analysis.national_snn / optimization.total_cost, 4)
            if optimization.total_cost > 0
            else 0,
            "alerts": len(analysis.alerts),
            "critical_alerts": len([a for a in analysis.alerts if a["level"] == "critique"]),
            "top_sector": analysis.sector_surpluses[0].sector if analysis.sector_surpluses else "N/A",
        }
