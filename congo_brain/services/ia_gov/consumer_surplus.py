"""Module 2: Consumer Surplus Engine.

Estime le CS pour chaque service public:
    CS = Disposition à payer - Prix payé

Variables mesurées:
    Prix payé, Qualité du service, Temps d'accès, Coûts indirects
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PublicService:
    """Service public avec mesures de surplus."""

    name: str
    willingness_to_pay: float = 0.0  # Disposition à payer (USD/mois)
    actual_price: float = 0.0  # Prix payé (USD/mois)
    quality_score: float = 0.0  # Qualité (0-10)
    access_time_hours: float = 0.0  # Temps d'accès (heures)
    indirect_cost: float = 0.0  # Coûts indirects (USD/mois)
    coverage_pct: float = 0.0  # Couverture population (%)
    satisfaction_pct: float = 0.0  # Satisfaction usagers (%)

    @property
    def consumer_surplus(self) -> float:
        """CS = WTP - Price - Indirect Costs."""
        return max(0, self.willingness_to_pay - self.actual_price - self.indirect_cost)

    @property
    def access_penalty(self) -> float:
        """Pénalité pour temps d'accès (>2h = pénalité)."""
        return max(0, (self.access_time_hours - 2) * 5)

    @property
    def quality_adjusted_cs(self) -> float:
        """CS ajusté par la qualité."""
        return self.consumer_surplus * (self.quality_score / 10)

    @property
    def effective_cs(self) -> float:
        """CS effectif = CS ajusté - pénalité accès."""
        return max(0, self.quality_adjusted_cs - self.access_penalty)

    @property
    def total_annual_benefit(self) -> float:
        """Bénéfice annuel pour la population couverte."""
        return self.effective_cs * 12

    def to_dict(self) -> dict:
        return {
            "service": self.name,
            "willingness_to_pay": round(self.willingness_to_pay, 2),
            "actual_price": round(self.actual_price, 2),
            "quality_score": round(self.quality_score, 1),
            "access_time_hours": round(self.access_time_hours, 1),
            "indirect_cost": round(self.indirect_cost, 2),
            "coverage_pct": round(self.coverage_pct, 1),
            "consumer_surplus": round(self.consumer_surplus, 2),
            "quality_adjusted_cs": round(self.quality_adjusted_cs, 2),
            "effective_cs": round(self.effective_cs, 2),
            "annual_benefit": round(self.total_annual_benefit, 2),
        }


# Services publics de base de la RDC
DRC_PUBLIC_SERVICES: list[dict] = [
    {
        "name": "Électricité",
        "willingness_to_pay": 25.0,
        "actual_price": 15.0,
        "quality_score": 3.0,
        "access_time_hours": 4.0,
        "indirect_cost": 8.0,
        "coverage_pct": 19.0,
        "satisfaction_pct": 25.0,
    },
    {
        "name": "Internet",
        "willingness_to_pay": 20.0,
        "actual_price": 12.0,
        "quality_score": 4.0,
        "access_time_hours": 1.0,
        "indirect_cost": 3.0,
        "coverage_pct": 23.0,
        "satisfaction_pct": 35.0,
    },
    {
        "name": "Eau potable",
        "willingness_to_pay": 15.0,
        "actual_price": 5.0,
        "quality_score": 5.0,
        "access_time_hours": 2.0,
        "indirect_cost": 2.0,
        "coverage_pct": 52.0,
        "satisfaction_pct": 40.0,
    },
    {
        "name": "Santé",
        "willingness_to_pay": 30.0,
        "actual_price": 8.0,
        "quality_score": 4.0,
        "access_time_hours": 6.0,
        "indirect_cost": 12.0,
        "coverage_pct": 45.0,
        "satisfaction_pct": 30.0,
    },
    {
        "name": "Transport",
        "willingness_to_pay": 10.0,
        "actual_price": 3.0,
        "quality_score": 3.5,
        "access_time_hours": 3.0,
        "indirect_cost": 5.0,
        "coverage_pct": 40.0,
        "satisfaction_pct": 28.0,
    },
    {
        "name": "Éducation",
        "willingness_to_pay": 20.0,
        "actual_price": 2.0,
        "quality_score": 4.5,
        "access_time_hours": 1.5,
        "indirect_cost": 4.0,
        "coverage_pct": 107.0,
        "satisfaction_pct": 45.0,
    },
    {
        "name": "Justice",
        "willingness_to_pay": 15.0,
        "actual_price": 5.0,
        "quality_score": 3.0,
        "access_time_hours": 8.0,
        "indirect_cost": 10.0,
        "coverage_pct": 30.0,
        "satisfaction_pct": 20.0,
    },
    {
        "name": "Sécurité alimentaire",
        "willingness_to_pay": 25.0,
        "actual_price": 18.0,
        "quality_score": 4.0,
        "access_time_hours": 2.0,
        "indirect_cost": 3.0,
        "coverage_pct": 60.0,
        "satisfaction_pct": 35.0,
    },
]


class ConsumerSurplusEngine:
    """Estime le Consumer Surplus pour les services publics de la RDC.

    CS = Disposition à payer - Prix - Coûts indirects
    """

    def __init__(self) -> None:
        self.services: dict[str, PublicService] = {}

    def load_baseline(self) -> None:
        for data in DRC_PUBLIC_SERVICES:
            ps = PublicService(**data)
            self.services[ps.name] = ps

    def add_service(self, service: PublicService) -> None:
        self.services[service.name] = service

    @property
    def total_cs(self) -> float:
        return sum(s.effective_cs for s in self.services.values())

    @property
    def average_cs(self) -> float:
        n = len(self.services)
        return self.total_cs / n if n > 0 else 0.0

    @property
    def average_quality(self) -> float:
        n = len(self.services)
        return sum(s.quality_score for s in self.services.values()) / n if n > 0 else 0.0

    @property
    def average_coverage(self) -> float:
        n = len(self.services)
        return sum(s.coverage_pct for s in self.services.values()) / n if n > 0 else 0.0

    def get_cs_ranking(self) -> list[dict]:
        """Classement des services par CS effectif."""
        return sorted([s.to_dict() for s in self.services.values()], key=lambda x: x["effective_cs"], reverse=True)

    def simulate_improvement(self, service_name: str, quality_delta: float = 0, price_delta: float = 0) -> dict:
        """Simule l'amélioration d'un service."""
        if service_name not in self.services:
            return {"error": f"Service {service_name} non trouvé"}

        s = self.services[service_name]
        original_cs = s.effective_cs

        s.quality_score = min(10, max(0, s.quality_score + quality_delta))
        s.actual_price = max(0, s.actual_price + price_delta)

        new_cs = s.effective_cs
        delta = new_cs - original_cs

        # Restore
        s.quality_score -= quality_delta
        s.actual_price -= price_delta

        return {
            "service": service_name,
            "original_cs": round(original_cs, 2),
            "new_cs": round(new_cs, 2),
            "cs_delta": round(delta, 2),
            "improvement_pct": round(delta / original_cs * 100, 1) if original_cs > 0 else 0,
        }

    def get_dashboard(self) -> dict:
        return {
            "model": "ConsumerSurplusEngine",
            "formula": "CS = WTP - Prix - Coûts indirects",
            "total_cs": round(self.total_cs, 2),
            "average_cs": round(self.average_cs, 2),
            "average_quality": round(self.average_quality, 1),
            "average_coverage": round(self.average_coverage, 1),
            "service_count": len(self.services),
            "services": self.get_cs_ranking(),
        }
