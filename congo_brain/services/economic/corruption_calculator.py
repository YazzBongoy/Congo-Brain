"""Corruption / Deadweight Loss Impact Calculator.

DWL = Corruption + Fraude + Retards administratifs + Coûts administratifs

Measures the deadweight loss caused by governance inefficiency.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DWLComponents:
    """Components of Deadweight Loss."""
    corruption: float = 0.0       # Direct corruption losses
    fraud: float = 0.0            # Financial fraud
    administrative_delays: float = 0.0  # Cost of delays
    administrative_costs: float = 0.0    # Bureaucratic overhead
    rent_seeking: float = 0.0     # Rent-seeking behavior
    tax_evasion: float = 0.0      # Tax evasion losses

    @property
    def total_dwl(self) -> float:
        return (
            self.corruption
            + self.fraud
            + self.administrative_delays
            + self.administrative_costs
            + self.rent_seeking
            + self.tax_evasion
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


# DRC DWL baseline estimates (billions USD, annual)
DRC_DWL_BASELINE = DWLComponents(
    corruption=2.5,
    fraud=1.2,
    administrative_delays=0.8,
    administrative_costs=0.6,
    rent_seeking=1.0,
    tax_evasion=1.5,
)


class CorruptionCalculator:
    """Calculates Deadweight Loss and its impact on national welfare.

    DWL = Corruption + Fraude + Retards + Coûts administratifs
    """

    def __init__(self) -> None:
        self.dwl = DRC_DWL_BASELINE
        self.total_economy: float = 55.0  # DRC GDP estimate (billions USD)

    def set_dwl(self, dwl: DWLComponents) -> None:
        self.dwl = dwl

    def set_gdp(self, gdp: float) -> None:
        self.total_economy = gdp

    @property
    def dwl_pct_gdp(self) -> float:
        if self.total_economy <= 0:
            return 0.0
        return round(self.dwl.total_dwl / self.total_economy * 100, 2)

    def get_component_breakdown(self) -> list[dict]:
        """Return DWL components as percentage of total DWL."""
        total = self.dwl.total_dwl
        components = {
            "Corruption": self.dwl.corruption,
            "Fraude": self.dwl.fraud,
            "Retards administratifs": self.dwl.administrative_delays,
            "Couts administratifs": self.dwl.administrative_costs,
            "Recherche de rentes": self.dwl.rent_seeking,
            "Evasion fiscale": self.dwl.tax_evasion,
        }
        breakdown = []
        for name, value in components.items():
            pct = round(value / total * 100, 1) if total > 0 else 0
            breakdown.append({
                "component": name,
                "value": round(value, 2),
                "percentage": pct,
                "impact_on_welfare": round(-value, 2),
            })
        breakdown.sort(key=lambda x: x["value"], reverse=True)
        return breakdown

    def scenario_analysis(self, reduction_pct: float) -> dict:
        """Simulate impact of reducing DWL by X%."""
        reduction = self.dwl.total_dwl * (reduction_pct / 100)
        new_dwl = self.dwl.total_dwl - reduction
        recovered_gdp_pct = round(reduction / self.total_economy * 100, 2) if self.total_economy > 0 else 0

        return {
            "scenario": f"Reduction de {reduction_pct}% du DWL",
            "current_dwl": round(self.dwl.total_dwl, 2),
            "new_dwl": round(new_dwl, 2),
            "reduction_amount": round(reduction, 2),
            "recovered_gdp_percentage": recovered_gdp_pct,
            "equivalent_to": f"{round(reduction, 1)} milliards USD recuperes pour l'economie",
        }

    def anti_corruption_targets(self) -> list[dict]:
        """Suggest targets for anti-corruption measures."""
        targets = [
            {
                "area": "Evasion fiscale",
                "current_loss": round(self.dwl.tax_evasion, 2),
                "target_reduction_pct": 50,
                "target_loss": round(self.dwl.tax_evasion * 0.5, 2),
                "potential_recovery": round(self.dwl.tax_evasion * 0.5, 2),
                "priority": "Haute" if self.dwl.tax_evasion > 1.0 else "Moyenne",
            },
            {
                "area": "Corruption directe",
                "current_loss": round(self.dwl.corruption, 2),
                "target_reduction_pct": 40,
                "target_loss": round(self.dwl.corruption * 0.6, 2),
                "potential_recovery": round(self.dwl.corruption * 0.4, 2),
                "priority": "Haute" if self.dwl.corruption > 2.0 else "Moyenne",
            },
            {
                "area": "Recherche de rentes",
                "current_loss": round(self.dwl.rent_seeking, 2),
                "target_reduction_pct": 30,
                "target_loss": round(self.dwl.rent_seeking * 0.7, 2),
                "potential_recovery": round(self.dwl.rent_seeking * 0.3, 2),
                "priority": "Haute" if self.dwl.rent_seeking > 1.0 else "Moyenne",
            },
            {
                "area": "Fraude",
                "current_loss": round(self.dwl.fraud, 2),
                "target_reduction_pct": 40,
                "target_loss": round(self.dwl.fraud * 0.6, 2),
                "potential_recovery": round(self.dwl.fraud * 0.4, 2),
                "priority": "Moyenne",
            },
        ]
        targets.sort(key=lambda x: x["potential_recovery"], reverse=True)
        return targets

    def get_dashboard(self) -> dict:
        return {
            "model": "CorruptionCalculator",
            "formula": "DWL = Corruption + Fraude + Retards + Couts + Rentes + Evasion",
            "dwl": self.dwl.to_dict(),
            "dwl_pct_gdp": self.dwl_pct_gdp,
            "total_gdp": self.total_economy,
            "breakdown": self.get_component_breakdown(),
            "scenarios": [
                self.scenario_analysis(10),
                self.scenario_analysis(25),
                self.scenario_analysis(50),
            ],
            "anti_corruption_targets": self.anti_corruption_targets(),
        }
