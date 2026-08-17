"""Module 4: National Resource Engine — Suivi détaillé mines/ressources.

Chaque mine = un objet avec:
    Nom, Province, Minerai, Réserves, Production, Valeur,
    Transformation locale, Taxes, Emplois, Exportations

Calculs:
    Valeur brute, Valeur ajoutée, Recettes fiscales,
    Effets économiques, Effets sociaux
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Mine:
    """Mine avec suivi complet de la chaîne de valeur."""
    name: str
    province: str
    mineral: str
    reserves_tons: float = 0.0       # Réserves estimées
    annual_production_tons: float = 0.0  # Production annuelle
    market_value_per_ton: float = 0.0 # Valeur marché (USD/tonne)
    local_processing_pct: float = 0.0 # % transformation locale
    tax_rate: float = 0.0            # Taux fiscal effectif (%)
    employees: int = 0
    export_value: float = 0.0        # Valeur exportations (M USD)
    local_processing_value: float = 0.0  # Valeur transformation locale

    @property
    def gross_value(self) -> float:
        """Valeur brute = Production × Prix."""
        return self.annual_production_tons * self.market_value_per_ton / 1_000_000

    @property
    def value_added(self) -> float:
        """Valeur ajoutée = Extraction + Transformation."""
        return self.gross_value * (1 + self.local_processing_pct / 100)

    @property
    def tax_revenue(self) -> float:
        """Recettes fiscales."""
        return self.gross_value * self.tax_rate / 100

    @property
    def net_national_value(self) -> float:
        """Valeur nette pour la nation."""
        return self.value_added - self.tax_revenue * 0.3  # 30% retourne en coûts

    @property
    def capture_rate(self) -> float:
        """Taux de capture de la valeur (locale / totale)."""
        total = self.gross_value + self.export_value
        return round((self.gross_value * self.local_processing_pct / 100) / total * 100, 1) if total > 0 else 0.0

    @property
    def jobs_per_million(self) -> float:
        """Emplois par million USD de valeur."""
        return round(self.employees / self.gross_value, 1) if self.gross_value > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "province": self.province,
            "mineral": self.mineral,
            "reserves_tons": self.reserves_tons,
            "annual_production_tons": self.annual_production_tons,
            "market_value_per_ton": self.market_value_per_ton,
            "gross_value": round(self.gross_value, 2),
            "value_added": round(self.value_added, 2),
            "tax_revenue": round(self.tax_revenue, 2),
            "net_national_value": round(self.net_national_value, 2),
            "local_processing_pct": self.local_processing_pct,
            "capture_rate": self.capture_rate,
            "employees": self.employees,
            "jobs_per_million": self.jobs_per_million,
        }


# Mines principales de la RDC
DRC_MINES: list[dict] = [
    {"name": "Kamoa-Kakula", "province": "Haut-Katanga", "mineral": "Cuivre",
     "reserves_tons": 43_000_000, "annual_production_tons": 500_000,
     "market_value_per_ton": 8_500, "local_processing_pct": 10, "tax_rate": 35,
     "employees": 4500, "export_value": 3_800, "local_processing_value": 400},
    {"name": "Tenke Fungurume", "province": "Haut-Katanga", "mineral": "Cobalt",
     "reserves_tons": 3_200_000, "annual_production_tons": 30_000,
     "market_value_per_ton": 35_000, "local_processing_pct": 5, "tax_rate": 30,
     "employees": 3500, "export_value": 1_000, "local_processing_value": 50},
    {"name": "Mutanda Mining", "province": "Haut-Katanga", "mineral": "Cobalt",
     "reserves_tons": 1_500_000, "annual_production_tons": 15_000,
     "market_value_per_ton": 35_000, "local_processing_pct": 3, "tax_rate": 30,
     "employees": 2000, "export_value": 500, "local_processing_value": 15},
    {"name": "Kibali Gold", "province": "Haut-Uélé", "mineral": "Or",
     "reserves_tons": 500, "annual_production_tons": 12,
     "market_value_per_ton": 60_000_000, "local_processing_pct": 8, "tax_rate": 40,
     "employees": 3000, "export_value": 650, "local_processing_value": 50},
    {"name": "Banro (Twangiza)", "province": "Sud-Kivu", "mineral": "Or",
     "reserves_tons": 200, "annual_production_tons": 5,
     "market_value_per_ton": 60_000_000, "local_processing_pct": 5, "tax_rate": 35,
     "employees": 1500, "export_value": 280, "local_processing_value": 15},
    {"name": "Sicomines", "province": "Haut-Katanga", "mineral": "Cuivre",
     "reserves_tons": 6_000_000, "annual_production_tons": 100_000,
     "market_value_per_ton": 8_500, "local_processing_pct": 15, "tax_rate": 35,
     "employees": 2500, "export_value": 800, "local_processing_value": 120},
    {"name": "AVZ Minerals (Manono)", "province": "Tanganyika", "mineral": "Lithium",
     "reserves_tons": 10_000_000, "annual_production_tons": 0,
     "market_value_per_ton": 25_000, "local_processing_pct": 2, "tax_rate": 30,
     "employees": 0, "export_value": 0, "local_processing_value": 0},
    {"name": "Somide (Coltan)", "province": "Sud-Kivu", "mineral": "Coltan",
     "reserves_tons": 50_000, "annual_production_tons": 500,
     "market_value_per_ton": 100_000, "local_processing_pct": 3, "tax_rate": 25,
     "employees": 800, "export_value": 45, "local_processing_value": 1.5},
]


class NationalResourceEngine:
    """Suivi détaillé des ressources naturelles de la RDC.

    Chaque mine est un objet avec calcul de valeur brute,
    valeur ajoutée, recettes fiscales, effets économiques/sociaux.
    """

    def __init__(self) -> None:
        self.mines: dict[str, Mine] = {}

    def load_baseline(self) -> None:
        for data in DRC_MINES:
            m = Mine(**data)
            self.mines[m.name] = m

    def add_mine(self, mine: Mine) -> None:
        self.mines[mine.name] = mine

    @property
    def total_gross_value(self) -> float:
        return sum(m.gross_value for m in self.mines.values())

    @property
    def total_value_added(self) -> float:
        return sum(m.value_added for m in self.mines.values())

    @property
    def total_tax_revenue(self) -> float:
        return sum(m.tax_revenue for m in self.mines.values())

    @property
    def total_employees(self) -> int:
        return sum(m.employees for m in self.mines.values())

    @property
    def overall_capture_rate(self) -> float:
        total = sum(m.gross_value + m.export_value for m in self.mines.values())
        local = sum(m.gross_value * m.local_processing_pct / 100 for m in self.mines.values())
        return round(local / total * 100, 1) if total > 0 else 0.0

    def get_mineral_breakdown(self) -> dict:
        """Breakdown par minerai."""
        minerals: dict[str, dict] = {}
        for m in self.mines.values():
            if m.mineral not in minerals:
                minerals[m.mineral] = {"production": 0, "value": 0, "mines": 0}
            minerals[m.mineral]["production"] += m.annual_production_tons
            minerals[m.mineral]["value"] += m.gross_value
            minerals[m.mineral]["mines"] += 1
        return minerals

    def compare_scenarios(self, mine_name: str, scenarios: list[dict]) -> list[dict]:
        """Compare transformation locale vs export brute."""
        if mine_name not in self.mines:
            return []

        m = self.mines[mine_name]
        results = []
        for s in scenarios:
            processing = s.get("local_processing_pct", m.local_processing_pct)
            original = m.local_processing_pct
            m.local_processing_pct = processing
            results.append({
                "scenario": s.get("name", f"Processing {processing}%"),
                "local_processing_pct": processing,
                "value_added": round(m.value_added, 2),
                "capture_rate": m.capture_rate,
                "nnv": round(m.net_national_value, 2),
            })
            m.local_processing_pct = original
        return results

    def get_dashboard(self) -> dict:
        return {
            "model": "NationalResourceEngine",
            "mine_count": len(self.mines),
            "total_gross_value": round(self.total_gross_value, 2),
            "total_value_added": round(self.total_value_added, 2),
            "total_tax_revenue": round(self.total_tax_revenue, 2),
            "total_employees": self.total_employees,
            "overall_capture_rate": self.overall_capture_rate,
            "mineral_breakdown": self.get_mineral_breakdown(),
            "mines": sorted([m.to_dict() for m in self.mines.values()],
                            key=lambda x: x["gross_value"], reverse=True),
        }
