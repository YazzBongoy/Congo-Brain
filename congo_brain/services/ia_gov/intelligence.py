"""IA GOV — Couche d'Intelligence Artificielle.

Analyse les données collectées et produit:
    - Scores de surplus (CS, PS, GR) par secteur/province
    - Détection d'anomalies budgétaires
    - Prévisions et tendances
    - Recommandations d'optimisation
    - Risques et alertes
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(str, Enum):
    CRITICAL = "critique"
    HIGH = "eleve"
    MEDIUM = "moyen"
    LOW = "faible"


class TrendDirection(str, Enum):
    IMPROVING = "en_amélioration"
    STABLE = "stable"
    DECLINING = "en_déclin"


@dataclass
class SurplusEstimate:
    """Estimation du surplus pour un secteur."""
    sector: str
    consumer_surplus: float = 0.0
    producer_surplus: float = 0.0
    government_revenue: float = 0.0
    natural_resource_value: float = 0.0
    deadweight_loss: float = 0.0
    environmental_cost: float = 0.0

    @property
    def snn(self) -> float:
        return (self.consumer_surplus + self.producer_surplus
                + self.government_revenue + self.natural_resource_value
                - self.deadweight_loss - self.environmental_cost)

    @property
    def efficiency(self) -> float:
        positive = self.consumer_surplus + self.producer_surplus + self.government_revenue
        return round(self.snn / positive * 100, 1) if positive > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "sector": self.sector,
            "cs": round(self.consumer_surplus, 2),
            "ps": round(self.producer_surplus, 2),
            "gr": round(self.government_revenue, 2),
            "nrv": round(self.natural_resource_value, 2),
            "dwl": round(self.deadweight_loss, 2),
            "ec": round(self.environmental_cost, 2),
            "snn": round(self.snn, 2),
            "efficiency": self.efficiency,
        }


@dataclass
class AnalysisResult:
    """Résultat complet de l'analyse IA."""
    timestamp: str = ""
    national_snn: float = 0.0
    sector_surpluses: list[SurplusEstimate] = field(default_factory=list)
    alerts: list[dict] = field(default_factory=list)
    trends: list[dict] = field(default_factory=list)
    recommendations: list[dict] = field(default_factory=list)
    decision_matrix: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "national_snn": round(self.national_snn, 2),
            "sector_count": len(self.sector_surpluses),
            "sectors": [s.to_dict() for s in self.sector_surpluses],
            "alerts_count": len(self.alerts),
            "alerts": self.alerts,
            "trends": self.trends,
            "recommendations_count": len(self.recommendations),
            "recommendations": self.recommendations,
            "decision_matrix": self.decision_matrix,
        }


class IntelligenceEngine:
    """Moteur d'IA pour l'analyse de gouvernance.

    Transforme les données brutes en estimations de surplus
    et recommandations d'optimisation.
    """

    # Sector elasticity assumptions (how responsive surplus is to spending)
    SECTOR_ELASTICITY: dict[str, dict] = {
        "Énergie": {"cs_elasticity": 1.5, "ps_elasticity": 1.8, "job_multiplier": 2.5},
        "Transport": {"cs_elasticity": 1.3, "ps_elasticity": 1.6, "job_multiplier": 3.0},
        "Santé": {"cs_elasticity": 2.0, "ps_elasticity": 0.5, "job_multiplier": 1.5},
        "Éducation": {"cs_elasticity": 1.8, "ps_elasticity": 0.8, "job_multiplier": 1.2},
        "Industrie minière": {"cs_elasticity": 0.5, "ps_elasticity": 2.5, "job_multiplier": 1.8},
        "Agriculture": {"cs_elasticity": 1.2, "ps_elasticity": 1.0, "job_multiplier": 2.0},
        "Numérique": {"cs_elasticity": 1.4, "ps_elasticity": 1.3, "job_multiplier": 1.5},
        "Forêt": {"cs_elasticity": 0.8, "ps_elasticity": 1.2, "job_multiplier": 1.0},
        "Eau": {"cs_elasticity": 2.5, "ps_elasticity": 0.3, "job_multiplier": 1.0},
    }

    # Corruption risk by sector
    CORRUPTION_RISK: dict[str, float] = {
        "Énergie": 0.6, "Transport": 0.7, "Santé": 0.4, "Éducation": 0.3,
        "Industrie minière": 0.8, "Agriculture": 0.3, "Numérique": 0.2,
        "Forêt": 0.6, "Eau": 0.5,
    }

    # Environmental impact by sector
    ENV_IMPACT: dict[str, float] = {
        "Énergie": 0.4, "Transport": 0.5, "Santé": 0.1, "Éducation": 0.1,
        "Industrie minière": 0.8, "Agriculture": 0.3, "Numérique": 0.1,
        "Forêt": 0.9, "Eau": 0.2,
    }

    def __init__(self) -> None:
        self.sectors: dict[str, dict] = {}

    def analyze(
        self,
        budget_data: dict,
        economic_data: dict,
        social_data: dict,
    ) -> AnalysisResult:
        """Analyse complète des données et estimation des surplus."""
        from datetime import datetime, timezone

        result = AnalysisResult(timestamp=datetime.now(timezone.utc).isoformat())

        gdp = economic_data.get("gdp", 55_000)
        total_spending = budget_data.get("total_expenditure", 14_000)
        tax_rev = budget_data.get("tax_revenue", 5_200)
        mining_rev = budget_data.get("mining_revenue", 3_500)

        sector_budgets = self._estimate_sector_budgets(total_spending)

        for sector_name, budget in sector_budgets.items():
            surplus = self._estimate_sector_surplus(sector_name, budget, gdp)
            result.sector_surpluses.append(surplus)

        result.national_snn = sum(s.snn for s in result.sector_surpluses)
        result.alerts = self._detect_alerts(budget_data, economic_data, social_data)
        result.trends = self._analyze_trends(economic_data, social_data)
        result.recommendations = self._generate_recommendations(result.sector_surpluses, budget_data, economic_data)
        result.decision_matrix = self._build_decision_matrix(result.sector_surpluses)

        return result

    def _estimate_sector_budgets(self, total_spending: float) -> dict[str, float]:
        """Estimate sectoral budget allocation based on DRC typical patterns."""
        allocations = {
            "Santé": 0.08,
            "Éducation": 0.10,
            "Transport": 0.12,
            "Énergie": 0.10,
            "Industrie minière": 0.08,
            "Agriculture": 0.07,
            "Sécurité": 0.15,
            "Économie": 0.05,
            "Administration": 0.15,
            "Autres": 0.10,
        }
        return {k: total_spending * v for k, v in allocations.items()}

    def _estimate_sector_surplus(self, sector: str, budget: float, gdp: float) -> SurplusEstimate:
        """Estimate CS, PS, GR, NRV, DWL, EC for a sector."""
        elasticity = self.SECTOR_ELASTICITY.get(sector, {"cs_elasticity": 1.0, "ps_elasticity": 1.0, "job_multiplier": 1.0})
        corruption = self.CORRUPTION_RISK.get(sector, 0.4)
        env = self.ENV_IMPACT.get(sector, 0.3)

        # Scale factor: budget relative to sector GDP share
        scale = budget / 1000  # normalize

        cs = budget * elasticity["cs_elasticity"] * 0.3 / 1000
        ps = budget * elasticity["ps_elasticity"] * 0.25 / 1000
        gr = budget * 0.15 / 1000  # government gets ~15% back in taxes

        # NRV only for resource sectors
        if sector in ("Industrie minière", "Forêt", "Agriculture"):
            nrv = budget * 0.5 / 1000
        else:
            nrv = 0.0

        dwl = budget * corruption * 0.2 / 1000
        ec = budget * env * 0.1 / 1000

        return SurplusEstimate(
            sector=sector,
            consumer_surplus=round(cs, 2),
            producer_surplus=round(ps, 2),
            government_revenue=round(gr, 2),
            natural_resource_value=round(nrv, 2),
            deadweight_loss=round(dwl, 2),
            environmental_cost=round(ec, 2),
        )

    def _detect_alerts(self, budget: dict, economic: dict, social: dict) -> list[dict]:
        """Detect governance alerts from data."""
        alerts = []
        deficit = budget.get("deficit", 0)
        revenue = budget.get("total_revenue", 1)
        inflation = economic.get("inflation", 0)
        execution = budget.get("execution_rate", 100)
        debt = budget.get("debt_stock", 0)
        gdp = economic.get("gdp", 1)
        poverty = social.get("poverty_rate", 0)
        electricity = social.get("access_electricity", 100)

        if deficit > revenue * 0.15:
            alerts.append({
                "type": "budget_deficit",
                "level": RiskLevel.CRITICAL.value,
                "message": f"Déficit budgétaire élevé: {deficit}M USD ({round(deficit/revenue*100,1)}% des recettes)",
                "sector": "Budget",
            })

        if inflation > 10:
            alerts.append({
                "type": "inflation",
                "level": RiskLevel.HIGH.value if inflation > 20 else RiskLevel.MEDIUM.value,
                "message": f"Inflation élevée: {inflation}%",
                "sector": "Économie",
            })

        if execution < 60:
            alerts.append({
                "type": "low_execution",
                "level": RiskLevel.HIGH.value,
                "message": f"Taux d'exécution faible: {execution}%",
                "sector": "Budget",
            })

        if debt / gdp > 0.5:
            alerts.append({
                "type": "debt_risk",
                "level": RiskLevel.HIGH.value,
                "message": f"Dette/PIB: {round(debt/gdp*100,1)}% (seuil: 60%)",
                "sector": "Fiscalité",
            })

        if poverty > 50:
            alerts.append({
                "type": "high_poverty",
                "level": RiskLevel.CRITICAL.value,
                "message": f"Taux de pauvreté critique: {poverty}%",
                "sector": "Social",
            })

        if electricity < 25:
            alerts.append({
                "type": "low_electricity",
                "level": RiskLevel.CRITICAL.value,
                "message": f"Accès électricité très faible: {electricity}%",
                "sector": "Énergie",
            })

        return alerts

    def _analyze_trends(self, economic: dict, social: dict) -> list[dict]:
        """Analyze trends from economic and social data."""
        trends = []
        gdp_growth = economic.get("gdp_growth", 0)
        inflation = economic.get("inflation", 0)
        poverty = social.get("poverty_rate", 0)

        trends.append({
            "indicator": "PIB",
            "value": gdp_growth,
            "trend": TrendDirection.IMPROVING.value if gdp_growth > 4 else TrendDirection.DECLINING.value if gdp_growth < 2 else TrendDirection.STABLE.value,
            "target": 7.0,
        })
        trends.append({
            "indicator": "Inflation",
            "value": inflation,
            "trend": TrendDirection.IMPROVING.value if inflation < 5 else TrendDirection.DECLINING.value if inflation > 15 else TrendDirection.STABLE.value,
            "target": 5.0,
        })
        trends.append({
            "indicator": "Pauvreté",
            "value": poverty,
            "trend": TrendDirection.IMPROVING.value if poverty < 50 else TrendDirection.DECLINING.value if poverty > 70 else TrendDirection.STABLE.value,
            "target": 30.0,
        })

        return trends

    def _generate_recommendations(
        self, surpluses: list[SurplusEstimate], budget: dict, economic: dict,
    ) -> list[dict]:
        """Generate optimization recommendations."""
        recs = []

        # Find sectors with highest DWL (corruption loss)
        high_dwl = sorted(surpluses, key=lambda s: s.deadweight_loss, reverse=True)
        if high_dwl and high_dwl[0].deadweight_loss > 0.5:
            recs.append({
                "type": "anti_corruption",
                "priority": "Haute",
                "sector": high_dwl[0].sector,
                "action": f"Réduire la corruption dans {high_dwl[0].sector} — perte estimée: {high_dwl[0].deadweight_loss}M USD",
                "impact": f"+{round(high_dwl[0].deadweight_loss * 0.5, 2)}M USD de SNN",
            })

        # Find sectors with highest CS potential
        high_cs = sorted(surpluses, key=lambda s: s.consumer_surplus, reverse=True)
        if high_cs:
            recs.append({
                "type": "consumer_surplus",
                "priority": "Haute",
                "sector": high_cs[0].sector,
                "action": f"Augmenter les investissements dans {high_cs[0].sector} — impact CS max",
                "impact": f"Amélioration du bien-être consommateur",
            })

        # Find sectors with NRV potential
        nrv_sectors = [s for s in surpluses if s.natural_resource_value > 0]
        if nrv_sectors:
            best_nrv = max(nrv_sectors, key=lambda s: s.natural_resource_value)
            recs.append({
                "type": "nrv_maximization",
                "priority": "Haute",
                "sector": best_nrv.sector,
                "action": f"Développer la transformation locale dans {best_nrv.sector}",
                "impact": f"NRV: +{round(best_nrv.natural_resource_value * 0.3, 2)}M USD",
            })

        # Environmental alert
        high_ec = sorted(surpluses, key=lambda s: s.environmental_cost, reverse=True)
        if high_ec and high_ec[0].environmental_cost > 0.5:
            recs.append({
                "type": "environmental",
                "priority": "Moyenne",
                "sector": high_ec[0].sector,
                "action": f"Réduire l'impact environnemental dans {high_ec[0].sector}",
                "impact": f"Réduction EC: {round(high_ec[0].environmental_cost * 0.3, 2)}M USD",
            })

        return recs

    def _build_decision_matrix(self, surpluses: list[SurplusEstimate]) -> list[dict]:
        """Build decision matrix: net benefit per sector."""
        matrix = []
        for s in surpluses:
            net_benefit = s.snn
            cost = s.deadweight_loss + s.environmental_cost
            benefit = s.consumer_surplus + s.producer_surplus + s.government_revenue + s.natural_resource_value
            matrix.append({
                "sector": s.sector,
                "benefit": round(benefit, 2),
                "cost": round(cost, 2),
                "net_benefit": round(net_benefit, 2),
                "ratio": round(benefit / cost, 2) if cost > 0 else float("inf"),
                "recommendation": "Investir" if net_benefit > 0 else "Réformer",
            })
        matrix.sort(key=lambda x: x["net_benefit"], reverse=True)
        return matrix
