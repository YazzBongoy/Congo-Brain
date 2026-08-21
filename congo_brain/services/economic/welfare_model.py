"""MOEG Core — Surplus National Net (SNN) Model.

Implements the extended welfare function for the DRC:

    SNN = CS + PS + GR + NRV - DWL - EC

where:
    CS  = Consumer Surplus (surplus des consommateurs)
    PS  = Producer Surplus (surplus des producteurs)
    GR  = Government Revenue (recettes publiques nettes)
    NRV = Natural Resource Value (valeur ajoutée des ressources)
    DWL = Deadweight Loss (corruption + monopoles + inefficacités)
    EC  = Environmental Cost (coût environnemental)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SectorWelfare:
    """Welfare contribution of a single economic sector."""

    sector: str
    consumer_surplus: float = 0.0
    producer_surplus: float = 0.0
    government_revenue: float = 0.0
    natural_resource_value: float = 0.0
    deadweight_loss: float = 0.0
    environmental_cost: float = 0.0

    @property
    def surpluses(self) -> float:
        return self.consumer_surplus + self.producer_surplus

    @property
    def positive_value(self) -> float:
        return self.consumer_surplus + self.producer_surplus + self.government_revenue + self.natural_resource_value

    @property
    def costs(self) -> float:
        return self.deadweight_loss + self.environmental_cost

    @property
    def snn(self) -> float:
        """Surplus National Net du secteur."""
        return self.positive_value - self.costs

    @property
    def corruption_rate(self) -> float:
        return round(self.deadweight_loss / self.positive_value * 100, 2) if self.positive_value > 0 else 0.0

    @property
    def environmental_rate(self) -> float:
        return round(self.environmental_cost / self.positive_value * 100, 2) if self.positive_value > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "sector": self.sector,
            "consumer_surplus": round(self.consumer_surplus, 2),
            "producer_surplus": round(self.producer_surplus, 2),
            "government_revenue": round(self.government_revenue, 2),
            "natural_resource_value": round(self.natural_resource_value, 2),
            "deadweight_loss": round(self.deadweight_loss, 2),
            "environmental_cost": round(self.environmental_cost, 2),
            "snn": round(self.snn, 2),
            "corruption_rate": self.corruption_rate,
            "environmental_rate": self.environmental_rate,
        }


@dataclass
class EconomyConstraints:
    """Macroeconomic constraints for the DRC."""

    budget_ceiling: float = 0.0
    revenue: float = 0.0
    max_debt_to_gdp: float = 60.0
    current_debt_to_gdp: float = 0.0
    max_inflation: float = 5.0
    current_inflation: float = 0.0
    gdp: float = 0.0

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
    """MOEG SNN welfare optimization model.

    Computes national Surplus National Net as:
        SNN = CS + PS + GR + NRV - DWL - EC
    """

    def __init__(self) -> None:
        self.sectors: dict[str, SectorWelfare] = {}
        self.constraints = EconomyConstraints()

    def add_sector(
        self,
        sector: str,
        cs: float,
        ps: float,
        revenue: float,
        nrv: float = 0.0,
        dwl: float = 0.0,
        ec: float = 0.0,
    ) -> SectorWelfare:
        sw = SectorWelfare(
            sector=sector,
            consumer_surplus=cs,
            producer_surplus=ps,
            government_revenue=revenue,
            natural_resource_value=nrv,
            deadweight_loss=dwl,
            environmental_cost=ec,
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
    def total_gr(self) -> float:
        return sum(s.government_revenue for s in self.sectors.values())

    @property
    def total_nrv(self) -> float:
        return sum(s.natural_resource_value for s in self.sectors.values())

    @property
    def total_dwl(self) -> float:
        return sum(s.deadweight_loss for s in self.sectors.values())

    @property
    def total_ec(self) -> float:
        return sum(s.environmental_cost for s in self.sectors.values())

    @property
    def total_positive(self) -> float:
        return self.total_cs + self.total_ps + self.total_gr + self.total_nrv

    @property
    def total_costs(self) -> float:
        return self.total_dwl + self.total_ec

    @property
    def total_snn(self) -> float:
        """Surplus National Net national."""
        return self.total_positive - self.total_costs

    @property
    def national_corruption_rate(self) -> float:
        return round(self.total_dwl / self.total_positive * 100, 2) if self.total_positive > 0 else 0.0

    @property
    def national_environmental_rate(self) -> float:
        return round(self.total_ec / self.total_positive * 100, 2) if self.total_positive > 0 else 0.0

    def get_sector_breakdown(self) -> list[dict]:
        return [s.to_dict() for s in sorted(self.sectors.values(), key=lambda x: x.snn, reverse=True)]

    def get_dashboard(self) -> dict:
        return {
            "model": "MOEG",
            "description": "Modele d'Optimisation Economique de la Gouvernance",
            "formula": "SNN = CS + PS + GR + NRV - DWL - EC",
            "total_snn": round(self.total_snn, 2),
            "components": {
                "consumer_surplus": round(self.total_cs, 2),
                "producer_surplus": round(self.total_ps, 2),
                "government_revenue": round(self.total_gr, 2),
                "natural_resource_value": round(self.total_nrv, 2),
                "deadweight_loss": round(self.total_dwl, 2),
                "environmental_cost": round(self.total_ec, 2),
            },
            "rates": {
                "corruption_rate": self.national_corruption_rate,
                "environmental_rate": self.national_environmental_rate,
            },
            "sector_count": len(self.sectors),
            "sectors": self.get_sector_breakdown(),
            "constraints": self.constraints.to_dict(),
        }
