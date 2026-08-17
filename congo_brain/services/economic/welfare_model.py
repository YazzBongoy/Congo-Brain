"""MOEG Core — Welfare Economics Model.

Implements the fundamental welfare function:

    max W = CS + PS + T - DWL

with sectoral decomposition and constraint handling for the DRC economy.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SectorWelfare:
    """Welfare contribution of a single economic sector."""
    sector: str
    consumer_surplus: float = 0.0
    producer_surplus: float = 0.0
    government_revenue: float = 0.0
    deadweight_loss: float = 0.0

    @property
    def net_welfare(self) -> float:
        return self.consumer_surplus + self.producer_surplus + self.government_revenue - self.deadweight_loss

    @property
    def corruption_rate(self) -> float:
        total = self.consumer_surplus + self.producer_surplus + self.government_revenue
        return round(self.deadweight_loss / total * 100, 2) if total > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "sector": self.sector,
            "consumer_surplus": round(self.consumer_surplus, 2),
            "producer_surplus": round(self.producer_surplus, 2),
            "government_revenue": round(self.government_revenue, 2),
            "deadweight_loss": round(self.deadweight_loss, 2),
            "net_welfare": round(self.net_welfare, 2),
            "corruption_rate": self.corruption_rate,
        }


@dataclass
class EconomyConstraints:
    """Macroeconomic constraints for the DRC."""
    budget_ceiling: float = 0.0           # Total government budget (D)
    revenue: float = 0.0                   # Total government revenue (R)
    max_debt_to_gdp: float = 60.0         # Debt/GDP ceiling (%)
    current_debt_to_gdp: float = 0.0      # Current debt/GDP (%)
    max_inflation: float = 5.0            # Inflation ceiling (%)
    current_inflation: float = 0.0        # Current inflation (%)
    gdp: float = 0.0                      # Gross Domestic Product

    @property
    def budget_deficit(self) -> float:
        return self.revenue - self.budget_ceiling

    @property
    def budget_balanced(self) -> bool:
        return self.budget_ceiling <= self.revenue

    @property
    def debt_sustainable(self) -> bool:
        return self.current_debt_to_gdp < self.max_debt_to_gdp

    @property
    def inflation_ok(self) -> bool:
        return self.current_inflation < self.max_inflation

    @property
    def all_constraints_met(self) -> bool:
        return self.budget_balanced and self.debt_sustainable and self.inflation_ok

    def to_dict(self) -> dict:
        return {
            "budget_ceiling": self.budget_ceiling,
            "revenue": self.revenue,
            "budget_deficit": round(self.budget_deficit, 2),
            "budget_balanced": self.budget_balanced,
            "debt_to_gdp": self.current_debt_to_gdp,
            "debt_ceiling": self.max_debt_to_gdp,
            "debt_sustainable": self.debt_sustainable,
            "inflation": self.current_inflation,
            "inflation_ceiling": self.max_inflation,
            "inflation_ok": self.inflation_ok,
            "gdp": self.gdp,
            "all_constraints_met": self.all_constraints_met,
        }


class WelfareModel:
    """MOEG welfare optimization model.

    Computes national welfare as:
        W = CS + PS + T - DWL

    with sectoral decomposition and constraint checking.
    """

    def __init__(self) -> None:
        self.sectors: dict[str, SectorWelfare] = {}
        self.constraints = EconomyConstraints()

    def add_sector(self, sector: str, cs: float, ps: float, revenue: float, dwl: float) -> SectorWelfare:
        """Add or update a sector's welfare contribution."""
        sw = SectorWelfare(
            sector=sector,
            consumer_surplus=cs,
            producer_surplus=ps,
            government_revenue=revenue,
            deadweight_loss=dwl,
        )
        self.sectors[sector] = sw
        return sw

    def set_constraints(self, constraints: EconomyConstraints) -> None:
        self.constraints = constraints

    @property
    def total_cs(self) -> float:
        return sum(s.consumer_surplus for s in self.sectors.values())

    @property
    def total_ps(self) -> float:
        return sum(s.producer_surplus for s in self.sectors.values())

    @property
    def total_revenue(self) -> float:
        return sum(s.government_revenue for s in self.sectors.values())

    @property
    def total_dwl(self) -> float:
        return sum(s.deadweight_loss for s in self.sectors.values())

    @property
    def total_welfare(self) -> float:
        return self.total_cs + self.total_ps + self.total_revenue - self.total_dwl

    @property
    def national_corruption_rate(self) -> float:
        total_positive = self.total_cs + self.total_ps + self.total_revenue
        return round(self.total_dwl / total_positive * 100, 2) if total_positive > 0 else 0.0

    def get_sector_breakdown(self) -> list[dict]:
        return [s.to_dict() for s in sorted(self.sectors.values(), key=lambda x: x.net_welfare, reverse=True)]

    def get_dashboard(self) -> dict:
        return {
            "model": "MOEG",
            "description": "Modele d'Optimisation Economique de la Gouvernance",
            "welfare_function": "W = CS + PS + T - DWL",
            "total_welfare": round(self.total_welfare, 2),
            "components": {
                "consumer_surplus": round(self.total_cs, 2),
                "producer_surplus": round(self.total_ps, 2),
                "government_revenue": round(self.total_revenue, 2),
                "deadweight_loss": round(self.total_dwl, 2),
            },
            "national_corruption_rate": self.national_corruption_rate,
            "sector_count": len(self.sectors),
            "sectors": self.get_sector_breakdown(),
            "constraints": self.constraints.to_dict(),
        }
