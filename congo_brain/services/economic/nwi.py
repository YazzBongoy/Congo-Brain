"""National Welfare Index (NWI) — Composite governance indicator.

NWI = 0.30 * CS_norm + 0.30 * PS_norm + 0.20 * Revenue_norm + 0.20 * Sustainability_norm

Each component is normalized to [0, 100].
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NWIComponents:
    """Raw components for NWI calculation."""
    consumer_surplus: float = 0.0
    producer_surplus: float = 0.0
    government_revenue: float = 0.0
    sustainability: float = 0.0
    # Reference values for normalization (max observed)
    max_cs: float = 1.0
    max_ps: float = 1.0
    max_revenue: float = 1.0
    max_sustainability: float = 1.0

    def normalize(self, value: float, max_val: float) -> float:
        if max_val <= 0:
            return 0.0
        return min(100.0, max(0.0, (value / max_val) * 100))

    @property
    def cs_normalized(self) -> float:
        return round(self.normalize(self.consumer_surplus, self.max_cs), 1)

    @property
    def ps_normalized(self) -> float:
        return round(self.normalize(self.producer_surplus, self.max_ps), 1)

    @property
    def revenue_normalized(self) -> float:
        return round(self.normalize(self.government_revenue, self.max_revenue), 1)

    @property
    def sustainability_normalized(self) -> float:
        return round(self.normalize(self.sustainability, self.max_sustainability), 1)


class NationalWelfareIndex:
    """NWI = 0.30*CS + 0.30*PS + 0.20*Revenue + 0.20*Sustainability

    Score 0-100:
        80-100: Excellent
        60-79:  Bon
        40-59:  Moyen
        20-39:  Faible
        0-19:   Critique
    """

    WEIGHTS = {
        "consumer_surplus": 0.30,
        "producer_surplus": 0.30,
        "government_revenue": 0.20,
        "sustainability": 0.20,
    }

    THRESHOLDS = [
        (80, "Excellent"),
        (60, "Bon"),
        (40, "Moyen"),
        (20, "Faible"),
        (0, "Critique"),
    ]

    def __init__(self) -> None:
        self.sector_scores: dict[str, NWIComponents] = {}

    def add_sector(self, name: str, components: NWIComponents) -> None:
        self.sector_scores[name] = components

    def compute_nwi(self, components: NWIComponents | None = None) -> dict:
        """Compute NWI from given components or aggregate from sectors."""
        if components is None:
            components = self._aggregate_sectors()

        cs_n = components.cs_normalized
        ps_n = components.ps_normalized
        rev_n = components.revenue_normalized
        sust_n = components.sustainability_normalized

        nwi = (
            self.WEIGHTS["consumer_surplus"] * cs_n
            + self.WEIGHTS["producer_surplus"] * ps_n
            + self.WEIGHTS["government_revenue"] * rev_n
            + self.WEIGHTS["sustainability"] * sust_n
        )

        rating = self._rate(nwi)

        return {
            "nwi_score": round(nwi, 2),
            "rating": rating,
            "components": {
                "consumer_surplus": {
                    "raw": round(components.consumer_surplus, 2),
                    "normalized": cs_n,
                    "weight": self.WEIGHTS["consumer_surplus"],
                    "weighted": round(self.WEIGHTS["consumer_surplus"] * cs_n, 2),
                },
                "producer_surplus": {
                    "raw": round(components.producer_surplus, 2),
                    "normalized": ps_n,
                    "weight": self.WEIGHTS["producer_surplus"],
                    "weighted": round(self.WEIGHTS["producer_surplus"] * ps_n, 2),
                },
                "government_revenue": {
                    "raw": round(components.government_revenue, 2),
                    "normalized": rev_n,
                    "weight": self.WEIGHTS["government_revenue"],
                    "weighted": round(self.WEIGHTS["government_revenue"] * rev_n, 2),
                },
                "sustainability": {
                    "raw": round(components.sustainability, 2),
                    "normalized": sust_n,
                    "weight": self.WEIGHTS["sustainability"],
                    "weighted": round(self.WEIGHTS["sustainability"] * sust_n, 2),
                },
            },
            "weights": self.WEIGHTS,
        }

    def compute_sector_nwi(self, sector: str) -> dict | None:
        if sector not in self.sector_scores:
            return None
        return self.compute_nwi(self.sector_scores[sector])

    def get_all_sectors(self) -> list[dict]:
        results = []
        for name, comp in self.sector_scores.items():
            result = self.compute_nwi(comp)
            result["sector"] = name
            results.append(result)
        results.sort(key=lambda x: x["nwi_score"], reverse=True)
        return results

    def _aggregate_sectors(self) -> NWIComponents:
        if not self.sector_scores:
            return NWIComponents()

        n = len(self.sector_scores)
        return NWIComponents(
            consumer_surplus=sum(c.consumer_surplus for c in self.sector_scores.values()) / n,
            producer_surplus=sum(c.producer_surplus for c in self.sector_scores.values()) / n,
            government_revenue=sum(c.government_revenue for c in self.sector_scores.values()) / n,
            sustainability=sum(c.sustainability for c in self.sector_scores.values()) / n,
            max_cs=sum(c.max_cs for c in self.sector_scores.values()) / n,
            max_ps=sum(c.max_ps for c in self.sector_scores.values()) / n,
            max_revenue=sum(c.max_revenue for c in self.sector_scores.values()) / n,
            max_sustainability=sum(c.max_sustainability for c in self.sector_scores.values()) / n,
        )

    def _rate(self, score: float) -> str:
        for threshold, label in self.THRESHOLDS:
            if score >= threshold:
                return label
        return "Critique"

    def get_dashboard(self) -> dict:
        overall = self.compute_nwi()
        return {
            "model": "NationalWelfareIndex",
            "formula": "NWI = 0.30*CS + 0.30*PS + 0.20*Recettes + 0.20*Durabilite",
            "overall": overall,
            "sector_count": len(self.sector_scores),
            "sectors": self.get_all_sectors(),
        }
