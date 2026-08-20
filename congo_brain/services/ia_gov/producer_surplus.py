"""Module 3: Producer Surplus Engine.

PS = Prix - Coût marginal

Variables:
    Coût de production, Fiscalité, Coût administratif,
    Corruption, Logistique, Accès énergie
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Enterprise:
    """Entreprise avec mesures de surplus."""

    name: str
    sector: str
    province: str = ""
    revenue: float = 0.0  # Revenus (M USD)
    production_cost: float = 0.0  # Coût de production
    tax_burden: float = 0.0  # Fiscalité (M USD)
    admin_cost: float = 0.0  # Coût administratif
    corruption_cost: float = 0.0  # Coût corruption
    logistics_cost: float = 0.0  # Coût logistique
    energy_cost: float = 0.0  # Coût énergie
    employees: int = 0
    formal: bool = True

    @property
    def total_cost(self) -> float:
        return (
            self.production_cost
            + self.tax_burden
            + self.admin_cost
            + self.corruption_cost
            + self.logistics_cost
            + self.energy_cost
        )

    @property
    def producer_surplus(self) -> float:
        """PS = Revenus - Coûts totaux."""
        return max(0, self.revenue - self.total_cost)

    @property
    def ps_margin(self) -> float:
        """Marge PS/Revenus."""
        return round(self.producer_surplus / self.revenue * 100, 1) if self.revenue > 0 else 0.0

    @property
    def corruption_drag(self) -> float:
        """Impact corruption sur PS (% du revenu)."""
        return round(self.corruption_cost / self.revenue * 100, 1) if self.revenue > 0 else 0.0

    @property
    def ps_per_employee(self) -> float:
        return round(self.producer_surplus / self.employees, 2) if self.employees > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "sector": self.sector,
            "province": self.province,
            "revenue": round(self.revenue, 2),
            "total_cost": round(self.total_cost, 2),
            "producer_surplus": round(self.producer_surplus, 2),
            "ps_margin": self.ps_margin,
            "corruption_drag": self.corruption_drag,
            "ps_per_employee": self.ps_per_employee,
            "employees": self.employees,
            "formal": self.formal,
        }


# Entreprises types de la RDC
DRC_ENTERPRISES: list[dict] = [
    {
        "name": "Gécamines",
        "sector": "Industrie minière",
        "province": "Haut-Katanga",
        "revenue": 2800,
        "production_cost": 1200,
        "tax_burden": 560,
        "admin_cost": 80,
        "corruption_cost": 200,
        "logistics_cost": 150,
        "energy_cost": 300,
        "employees": 12000,
    },
    {
        "name": "SNEL",
        "sector": "Énergie",
        "province": "Kinshasa",
        "revenue": 800,
        "production_cost": 600,
        "tax_burden": 120,
        "admin_cost": 60,
        "corruption_cost": 100,
        "logistics_cost": 40,
        "energy_cost": 0,
        "employees": 8000,
    },
    {
        "name": "Regideso",
        "sector": "Eau",
        "province": "Kinshasa",
        "revenue": 150,
        "production_cost": 120,
        "tax_burden": 20,
        "admin_cost": 25,
        "corruption_cost": 30,
        "logistics_cost": 10,
        "energy_cost": 20,
        "employees": 3000,
    },
    {
        "name": "Vodacom RDC",
        "sector": "Télécommunications",
        "province": "Kinshasa",
        "revenue": 1200,
        "production_cost": 500,
        "tax_burden": 200,
        "admin_cost": 50,
        "corruption_cost": 30,
        "logistics_cost": 80,
        "energy_cost": 100,
        "employees": 2500,
    },
    {
        "name": "Socir (pétrole)",
        "sector": "Pétrole",
        "province": "Kongo Central",
        "revenue": 3500,
        "production_cost": 1800,
        "tax_burden": 700,
        "admin_cost": 100,
        "corruption_cost": 250,
        "logistics_cost": 200,
        "energy_cost": 150,
        "employees": 5000,
    },
    {
        "name": "BRAKIT (ciment)",
        "sector": "Industrie",
        "province": "Kongo Central",
        "revenue": 200,
        "production_cost": 130,
        "tax_burden": 30,
        "admin_cost": 15,
        "corruption_cost": 15,
        "logistics_cost": 20,
        "energy_cost": 25,
        "employees": 800,
    },
    {
        "name": "PME agricole type",
        "sector": "Agriculture",
        "province": "Kasaï",
        "revenue": 50,
        "production_cost": 25,
        "tax_burden": 8,
        "admin_cost": 5,
        "corruption_cost": 4,
        "logistics_cost": 6,
        "energy_cost": 2,
        "employees": 15,
    },
    {
        "name": "Restaurant formel",
        "sector": "Services",
        "province": "Kinshasa",
        "revenue": 30,
        "production_cost": 15,
        "tax_burden": 5,
        "admin_cost": 3,
        "corruption_cost": 2,
        "logistics_cost": 2,
        "energy_cost": 3,
        "employees": 8,
    },
]


class ProducerSurplusEngine:
    """Estime le Producer Surplus pour les entreprises de la RDC.

    PS = Prix - Coût marginal
    """

    def __init__(self) -> None:
        self.enterprises: dict[str, Enterprise] = {}

    def load_baseline(self) -> None:
        for data in DRC_ENTERPRISES:
            e = Enterprise(**data)
            self.enterprises[e.name] = e

    def add_enterprise(self, enterprise: Enterprise) -> None:
        self.enterprises[enterprise.name] = enterprise

    @property
    def total_ps(self) -> float:
        return sum(e.producer_surplus for e in self.enterprises.values())

    @property
    def total_revenue(self) -> float:
        return sum(e.revenue for e in self.enterprises.values())

    @property
    def total_employees(self) -> int:
        return sum(e.employees for e in self.enterprises.values())

    @property
    def average_margin(self) -> float:
        revenues = [e.revenue for e in self.enterprises.values() if e.revenue > 0]
        if not revenues:
            return 0.0
        return sum(e.ps_margin for e in self.enterprises.values() if e.revenue > 0) / len(revenues)

    @property
    def total_corruption_drag(self) -> float:
        return sum(e.corruption_cost for e in self.enterprises.values())

    def simulate_reform(
        self, reform_name: str, tax_reduction: float = 0, admin_reduction: float = 0, corruption_reduction: float = 0
    ) -> dict:
        """Simule l'impact d'une réforme sur le PS."""
        original_ps = {name: e.producer_surplus for name, e in self.enterprises.items()}

        for e in self.enterprises.values():
            e.tax_burden = max(0, e.tax_burden * (1 - tax_reduction))
            e.admin_cost = max(0, e.admin_cost * (1 - admin_reduction))
            e.corruption_cost = max(0, e.corruption_cost * (1 - corruption_reduction))

        new_ps = {name: e.producer_surplus for name, e in self.enterprises.items()}
        delta = sum(new_ps.values()) - sum(original_ps.values())

        # Restore
        for data in DRC_ENTERPRISES:
            e = self.enterprises[data["name"]]
            e.tax_burden = data["tax_burden"]
            e.admin_cost = data["admin_cost"]
            e.corruption_cost = data["corruption_cost"]

        return {
            "reform": reform_name,
            "original_total_ps": round(sum(original_ps.values()), 2),
            "new_total_ps": round(sum(new_ps.values()), 2),
            "ps_delta": round(delta, 2),
            "improvement_pct": round(delta / sum(original_ps.values()) * 100, 1)
            if sum(original_ps.values()) > 0
            else 0,
        }

    def get_ps_ranking(self) -> list[dict]:
        return sorted(
            [e.to_dict() for e in self.enterprises.values()], key=lambda x: x["producer_surplus"], reverse=True
        )

    def get_dashboard(self) -> dict:
        return {
            "model": "ProducerSurplusEngine",
            "formula": "PS = Revenus - Coûts totaux",
            "total_ps": round(self.total_ps, 2),
            "total_revenue": round(self.total_revenue, 2),
            "total_employees": self.total_employees,
            "average_margin": round(self.average_margin, 1),
            "total_corruption_drag": round(self.total_corruption_drag, 2),
            "enterprise_count": len(self.enterprises),
            "enterprises": self.get_ps_ranking(),
        }
