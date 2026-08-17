"""Corruption / Deadweight Loss + Environmental Cost Calculator.

SNN costs = DWL + EC
    DWL = Corruption + Fraude + Retards administratifs + Coûts administratifs + Rentes + Évasion fiscale
    EC  = Impact environnemental des activités économiques
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DWLComponents:
    """Components of Deadweight Loss."""
    corruption: float = 0.0
    fraud: float = 0.0
    administrative_delays: float = 0.0
    administrative_costs: float = 0.0
    rent_seeking: float = 0.0
    tax_evasion: float = 0.0

    @property
    def total_dwl(self) -> float:
        return (
            self.corruption + self.fraud + self.administrative_delays
            + self.administrative_costs + self.rent_seeking + self.tax_evasion
        )

    def to_dict(self) -> dict:
        return {
            "corruption": round(self.corruption, 2),
            "fraud": round(self.fraud, 2),
            "administrative_delays": round(self.administrative_delays, 2),
            "administrative_costs": round(self.administrative_costs, 2),
            "rent_seeking": round(self.rent_seeking, 2),
            "tax_evasion": round(self.tax_evasion, 2),
            "total_dwl": round(self.total_dwl, 2),
        }


@dataclass
class EnvironmentalCost:
    """Environmental cost components."""
    deforestation: float = 0.0
    pollution: float = 0.0
    water_contamination: float = 0.0
    soil_degradation: float = 0.0
    biodiversity_loss: float = 0.0
    carbon_emissions: float = 0.0

    @property
    def total_ec(self) -> float:
        return (
            self.deforestation + self.pollution + self.water_contamination
            + self.soil_degradation + self.biodiversity_loss + self.carbon_emissions
        )

    def to_dict(self) -> dict:
        return {
            "deforestation": round(self.deforestation, 2),
            "pollution": round(self.pollution, 2),
            "water_contamination": round(self.water_contamination, 2),
            "soil_degradation": round(self.soil_degradation, 2),
            "biodiversity_loss": round(self.biodiversity_loss, 2),
            "carbon_emissions": round(self.carbon_emissions, 2),
            "total_ec": round(self.total_ec, 2),
        }


# DRC baseline estimates (billions USD, annual)
DRC_DWL_BASELINE = DWLComponents(
    corruption=2.5, fraud=1.2, administrative_delays=0.8,
    administrative_costs=0.6, rent_seeking=1.0, tax_evasion=1.5,
)

DRC_EC_BASELINE = EnvironmentalCost(
    deforestation=1.2, pollution=0.8, water_contamination=0.5,
    soil_degradation=0.4, biodiversity_loss=0.6, carbon_emissions=0.9,
)


class CorruptionCalculator:
    """Calculates SNN cost components: DWL + Environmental Cost."""

    def __init__(self) -> None:
        self.dwl = DRC_DWL_BASELINE
        self.ec = DRC_EC_BASELINE
        self.total_economy: float = 55.0

    def set_dwl(self, dwl: DWLComponents) -> None:
        self.dwl = dwl

    def set_ec(self, ec: EnvironmentalCost) -> None:
        self.ec = ec

    def set_gdp(self, gdp: float) -> None:
        self.total_economy = gdp

    @property
    def total_costs(self) -> float:
        """SNN costs = DWL + EC."""
        return self.dwl.total_dwl + self.ec.total_ec

    @property
    def costs_pct_gdp(self) -> float:
        if self.total_economy <= 0:
            return 0.0
        return round(self.total_costs / self.total_economy * 100, 2)

    @property
    def dwl_pct_gdp(self) -> float:
        if self.total_economy <= 0:
            return 0.0
        return round(self.dwl.total_dwl / self.total_economy * 100, 2)

    @property
    def ec_pct_gdp(self) -> float:
        if self.total_economy <= 0:
            return 0.0
        return round(self.ec.total_ec / self.total_economy * 100, 2)

    def get_component_breakdown(self) -> list[dict]:
        total = self.total_costs
        components = {
            "Corruption": self.dwl.corruption,
            "Fraude": self.dwl.fraud,
            "Retards administratifs": self.dwl.administrative_delays,
            "Couts administratifs": self.dwl.administrative_costs,
            "Recherche de rentes": self.dwl.rent_seeking,
            "Evasion fiscale": self.dwl.tax_evasion,
            "Deforestation": self.ec.deforestation,
            "Pollution": self.ec.pollution,
            "Contamination eau": self.ec.water_contamination,
            "Degradation sols": self.ec.soil_degradation,
            "Perte biodiversite": self.ec.biodiversity_loss,
            "Emissions carbone": self.ec.carbon_emissions,
        }
        breakdown = []
        for name, value in components.items():
            pct = round(value / total * 100, 1) if total > 0 else 0
            category = "DWL" if name in {
                "Corruption", "Fraude", "Retards administratifs",
                "Couts administratifs", "Recherche de rentes", "Evasion fiscale",
            } else "EC"
            breakdown.append({
                "component": name,
                "category": category,
                "value": round(value, 2),
                "percentage": pct,
                "impact_on_snn": round(-value, 2),
            })
        breakdown.sort(key=lambda x: x["value"], reverse=True)
        return breakdown

    def scenario_analysis(self, dwl_reduction_pct: float = 0.0, ec_reduction_pct: float = 0.0) -> dict:
        dwl_reduction = self.dwl.total_dwl * (dwl_reduction_pct / 100)
        ec_reduction = self.ec.total_ec * (ec_reduction_pct / 100)
        total_reduction = dwl_reduction + ec_reduction
        recovered_gdp_pct = round(total_reduction / self.total_economy * 100, 2) if self.total_economy > 0 else 0

        return {
            "scenario": f"DWL -{dwl_reduction_pct}%, EC -{ec_reduction_pct}%",
            "current_costs": round(self.total_costs, 2),
            "reduction_amount": round(total_reduction, 2),
            "new_costs": round(self.total_costs - total_reduction, 2),
            "recovered_gdp_percentage": recovered_gdp_pct,
            "snn_improvement": round(total_reduction, 2),
        }

    def anti_corruption_targets(self) -> list[dict]:
        targets = [
            {
                "area": "Evasion fiscale",
                "current_loss": round(self.dwl.tax_evasion, 2),
                "target_reduction_pct": 50,
                "potential_recovery": round(self.dwl.tax_evasion * 0.5, 2),
                "priority": "Haute",
            },
            {
                "area": "Corruption directe",
                "current_loss": round(self.dwl.corruption, 2),
                "target_reduction_pct": 40,
                "potential_recovery": round(self.dwl.corruption * 0.4, 2),
                "priority": "Haute",
            },
            {
                "area": "Recherche de rentes",
                "current_loss": round(self.dwl.rent_seeking, 2),
                "target_reduction_pct": 30,
                "potential_recovery": round(self.dwl.rent_seeking * 0.3, 2),
                "priority": "Moyenne",
            },
        ]
        targets.sort(key=lambda x: x["potential_recovery"], reverse=True)
        return targets

    def environmental_targets(self) -> list[dict]:
        targets = [
            {
                "area": "Deforestation",
                "current_cost": round(self.ec.deforestation, 2),
                "target_reduction_pct": 40,
                "potential_recovery": round(self.ec.deforestation * 0.4, 2),
                "priority": "Haute",
            },
            {
                "area": "Emissions carbone",
                "current_cost": round(self.ec.carbon_emissions, 2),
                "target_reduction_pct": 30,
                "potential_recovery": round(self.ec.carbon_emissions * 0.3, 2),
                "priority": "Moyenne",
            },
            {
                "area": "Pollution",
                "current_cost": round(self.ec.pollution, 2),
                "target_reduction_pct": 35,
                "potential_recovery": round(self.ec.pollution * 0.35, 2),
                "priority": "Moyenne",
            },
        ]
        targets.sort(key=lambda x: x["potential_recovery"], reverse=True)
        return targets

    def get_dashboard(self) -> dict:
        return {
            "model": "CorruptionCalculator",
            "formula": "SNN_costs = DWL + EC",
            "dw": self.dwl.to_dict(),
            "ec": self.ec.to_dict(),
            "total_costs": round(self.total_costs, 2),
            "total_costs_pct_gdp": self.costs_pct_gdp,
            "dwl_pct_gdp": self.dwl_pct_gdp,
            "ec_pct_gdp": self.ec_pct_gdp,
            "total_gdp": self.total_economy,
            "breakdown": self.get_component_breakdown(),
            "scenarios": [
                self.scenario_analysis(dwl_reduction_pct=10, ec_reduction_pct=10),
                self.scenario_analysis(dwl_reduction_pct=25, ec_reduction_pct=25),
                self.scenario_analysis(dwl_reduction_pct=50, ec_reduction_pct=50),
            ],
            "anti_corruption_targets": self.anti_corruption_targets(),
            "environmental_targets": self.environmental_targets(),
        }
