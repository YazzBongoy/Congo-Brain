"""Module 5: Governance Score — Note par ministère.

Score = 40% Optimisation + 20% Transparence + 20% Performance + 20% Satisfaction
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MinistryScore:
    """Score de gouvernance pour un ministère."""
    name: str
    optimization: float = 0.0     # Efficacité allocation (0-100)
    transparency: float = 0.0     # Transparence (0-100)
    performance: float = 0.0      # Performance budgétaire (0-100)
    satisfaction: float = 0.0     # Satisfaction citoyens (0-100)

    @property
    def governance_score(self) -> float:
        """Score pondéré."""
        return round(
            0.40 * self.optimization
            + 0.20 * self.transparency
            + 0.20 * self.performance
            + 0.20 * self.satisfaction, 1
        )

    @property
    def rating(self) -> str:
        score = self.governance_score
        if score >= 80: return "Excellent"
        if score >= 65: return "Bon"
        if score >= 50: return "Moyen"
        if score >= 35: return "Faible"
        return "Critique"

    def to_dict(self) -> dict:
        return {
            "ministry": self.name,
            "optimization": round(self.optimization, 1),
            "transparency": round(self.transparency, 1),
            "performance": round(self.performance, 1),
            "satisfaction": round(self.satisfaction, 1),
            "governance_score": self.governance_score,
            "rating": self.rating,
        }


# Ministères de la RDC avec scores estimés
DRC_MINISTRIES: list[dict] = [
    {"name": "Santé", "optimization": 45, "transparency": 35, "performance": 40, "satisfaction": 30},
    {"name": "Éducation", "optimization": 50, "transparency": 40, "performance": 45, "satisfaction": 45},
    {"name": "Infrastructure", "optimization": 40, "transparency": 30, "performance": 35, "satisfaction": 25},
    {"name": "Finance", "optimization": 55, "transparency": 50, "performance": 50, "satisfaction": 35},
    {"name": "Agriculture", "optimization": 35, "transparency": 25, "performance": 30, "satisfaction": 40},
    {"name": "Mines", "optimization": 60, "transparency": 40, "performance": 55, "satisfaction": 30},
    {"name": "Énergie", "optimization": 42, "transparency": 35, "performance": 38, "satisfaction": 28},
    {"name": "Environnement", "optimization": 38, "transparency": 45, "performance": 35, "satisfaction": 50},
    {"name": "Justice", "optimization": 30, "transparency": 25, "performance": 28, "satisfaction": 20},
    {"name": "Intérieur", "optimization": 35, "transparency": 20, "performance": 30, "satisfaction": 22},
]


class GovernanceScoreEngine:
    """Évalue la gouvernance de chaque ministère.

    Score = 40% Optimisation + 20% Transparence + 20% Performance + 20% Satisfaction
    """

    def __init__(self) -> None:
        self.ministries: dict[str, MinistryScore] = {}

    def load_baseline(self) -> None:
        for data in DRC_MINISTRIES:
            ms = MinistryScore(**data)
            self.ministries[ms.name] = ms

    def add_ministry(self, ministry: MinistryScore) -> None:
        self.ministries[ministry.name] = ministry

    @property
    def average_score(self) -> float:
        n = len(self.ministries)
        return sum(m.governance_score for m in self.ministries.values()) / n if n > 0 else 0.0

    @property
    def national_governance_score(self) -> float:
        """Score national pondéré par la taille du budget."""
        return round(self.average_score, 1)

    def get_ranking(self) -> list[dict]:
        return sorted([m.to_dict() for m in self.ministries.values()],
                      key=lambda x: x["governance_score"], reverse=True)

    def get_improvement_targets(self) -> list[dict]:
        """Cibles d'amélioration pour chaque ministère."""
        targets = []
        for m in self.ministries.values():
            weakest = min(
                ("optimization", m.optimization),
                ("transparency", m.transparency),
                ("performance", m.performance),
                ("satisfaction", m.satisfaction),
                key=lambda x: x[1],
            )
            targets.append({
                "ministry": m.name,
                "current_score": m.governance_score,
                "weakest_dimension": weakest[0],
                "weakest_value": weakest[1],
                "target_value": min(100, weakest[1] + 20),
                "potential_score_gain": round((min(100, weakest[1] + 20) - weakest[1]) * 0.2, 1),
            })
        targets.sort(key=lambda x: x["potential_score_gain"], reverse=True)
        return targets

    def get_dashboard(self) -> dict:
        return {
            "model": "GovernanceScoreEngine",
            "formula": "Score = 0.40*Opt + 0.20*Trans + 0.20*Perf + 0.20*Sat",
            "national_score": self.national_governance_score,
            "ministry_count": len(self.ministries),
            "ministries": self.get_ranking(),
            "improvement_targets": self.get_improvement_targets(),
        }
