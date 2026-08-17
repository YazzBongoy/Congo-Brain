"""IA GOV — Couche de Collecte des Données.

Collecte et structure les données de:
    - Budget national (recettes, dépenses, exécution)
    - Économie (PIB, inflation, taux de change, balance commerciale)
    - Social (emploi, santé, éducation, accès eau/énergie)
    - Ressources naturelles (extraction, transformation, exportation)
    - Sécurité (incidents, zones à risque)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BudgetData:
    """Données budgétaires nationales."""
    year: int
    total_revenue: float = 0.0          # Recettes totales (M USD)
    tax_revenue: float = 0.0            # Recettes fiscales
    customs_revenue: float = 0.0        # Recettes douanières
    mining_revenue: float = 0.0         # Recettes minières
    other_revenue: float = 0.0          # Autres recettes
    total_expenditure: float = 0.0      # Dépenses totales
    current_expenditure: float = 0.0    # Dépenses courantes
    capital_expenditure: float = 0.0    # Dépenses d'investissement
    execution_rate: float = 0.0         # Taux d'exécution (%)
    deficit: float = 0.0               # Déficit budgétaire
    debt_stock: float = 0.0            # Stock de dette

    @property
    def budget_balance(self) -> float:
        return self.total_revenue - self.total_expenditure

    @property
    def tax_to_gdp(self) -> float:
        """Will be computed when GDP is available."""
        return 0.0

    def to_dict(self) -> dict:
        return {
            "year": self.year,
            "total_revenue": round(self.total_revenue, 2),
            "tax_revenue": round(self.tax_revenue, 2),
            "customs_revenue": round(self.customs_revenue, 2),
            "mining_revenue": round(self.mining_revenue, 2),
            "total_expenditure": round(self.total_expenditure, 2),
            "current_expenditure": round(self.current_expenditure, 2),
            "capital_expenditure": round(self.capital_expenditure, 2),
            "execution_rate": round(self.execution_rate, 1),
            "deficit": round(self.deficit, 2),
            "debt_stock": round(self.debt_stock, 2),
            "budget_balance": round(self.budget_balance, 2),
        }


@dataclass
class EconomicData:
    """Données macroéconomiques."""
    year: int
    gdp: float = 0.0                    # PIB (M USD)
    gdp_growth: float = 0.0            # Croissance PIB (%)
    inflation: float = 0.0             # Inflation (%)
    exchange_rate: float = 0.0         # Taux de change
    unemployment: float = 0.0          # Chômage (%)
    trade_balance: float = 0.0         # Balance commerciale (M USD)
    fdi_inflow: float = 0.0            # IDE entrants (M USD)
    remittances: float = 0.0           # Transferts (M USD)
    informal_sector_pct: float = 0.0   # Secteur informel (% PIB)
    # Sectoral GDP
    agriculture_gdp: float = 0.0
    mining_gdp: float = 0.0
    industry_gdp: float = 0.0
    services_gdp: float = 0.0
    energy_gdp: float = 0.0

    @property
    def gdp_per_capita(self) -> float:
        return 0.0  # Will be computed with population

    def to_dict(self) -> dict:
        return {
            "year": self.year,
            "gdp": round(self.gdp, 2),
            "gdp_growth": round(self.gdp_growth, 1),
            "inflation": round(self.inflation, 1),
            "unemployment": round(self.unemployment, 1),
            "trade_balance": round(self.trade_balance, 2),
            "fdi_inflow": round(self.fdi_inflow, 2),
            "informal_sector_pct": round(self.informal_sector_pct, 1),
            "sectoral_gdp": {
                "agriculture": round(self.agriculture_gdp, 2),
                "mining": round(self.mining_gdp, 2),
                "industry": round(self.industry_gdp, 2),
                "services": round(self.services_gdp, 2),
                "energy": round(self.energy_gdp, 2),
            },
        }


@dataclass
class SocialData:
    """Données sociales et humaines."""
    year: int
    population: float = 0.0            # Population (millions)
    population_growth: float = 0.0     # Croissance démographique (%)
    poverty_rate: float = 0.0          # Taux de pauvreté (%)
    life_expectancy: float = 0.0       # Espérance de vie
    literacy_rate: float = 0.0         # Taux d'alphabétisation (%)
    school_enrollment: float = 0.0     # Taux de scolarisation (%)
    health_expenditure_pct: float = 0.0  # Dépenses santé (% PIB)
    education_expenditure_pct: float = 0.0  # Dépenses éducation (% PIB)
    access_electricity: float = 0.0    # Accès électricité (%)
    access_water: float = 0.0          # Accès eau potable (%)
    access_internet: float = 0.0       # Accès internet (%)
    mobile_penetration: float = 0.0    # Pénétration mobile (%)
    under5_mortality: float = 0.0      # Mortalité <5 ans (pour 1000)
    gini_coefficient: float = 0.0      # Coefficient de Gini

    def to_dict(self) -> dict:
        return {
            "year": self.year,
            "population": round(self.population, 2),
            "poverty_rate": round(self.poverty_rate, 1),
            "life_expectancy": round(self.life_expectancy, 1),
            "literacy_rate": round(self.literacy_rate, 1),
            "school_enrollment": round(self.school_enrollment, 1),
            "access_electricity": round(self.access_electricity, 1),
            "access_water": round(self.access_water, 1),
            "access_internet": round(self.access_internet, 1),
            "under5_mortality": round(self.under5_mortality, 1),
            "gini": round(self.gini_coefficient, 2),
        }


class DataCollector:
    """Collecte et agrège les données pour l'IA GOV.

    Fournit des données réalistes basées sur les statistiques de la RDC.
    """

    def __init__(self) -> None:
        self.budget: BudgetData | None = None
        self.economy: EconomicData | None = None
        self.social: SocialData | None = None
        self.province_data: dict[str, dict] = {}

    def load_drc_baseline(self, year: int = 2024) -> None:
        """Charge les données de base de la RDC."""
        self.budget = BudgetData(
            year=year,
            total_revenue=12_500,
            tax_revenue=5_200,
            customs_revenue=2_800,
            mining_revenue=3_500,
            other_revenue=1_000,
            total_expenditure=14_000,
            current_expenditure=9_800,
            capital_expenditure=4_200,
            execution_rate=72.0,
            deficit=1_500,
            debt_stock=6_500,
        )
        self.economy = EconomicData(
            year=year,
            gdp=55_000,
            gdp_growth=6.1,
            inflation=12.5,
            exchange_rate=2800.0,
            unemployment=28.0,
            trade_balance=2_500,
            fdi_inflow=1_800,
            remittances=500,
            informal_sector_pct=80.0,
            agriculture_gdp=11_000,
            mining_gdp=13_200,
            industry_gdp=12_100,
            services_gdp=15_400,
            energy_gdp=3_300,
        )
        self.social = SocialData(
            year=year,
            population=102.0,
            population_growth=3.2,
            poverty_rate=62.0,
            life_expectancy=61.0,
            literacy_rate=77.0,
            school_enrollment=107.0,
            health_expenditure_pct=3.5,
            education_expenditure_pct=2.8,
            access_electricity=19.0,
            access_water=52.0,
            access_internet=23.0,
            mobile_penetration=43.0,
            under5_mortality=88.0,
            gini_coefficient=0.42,
        )
        self._load_province_data()

    def _load_province_data(self) -> None:
        self.province_data = {
            "Kinshasa": {"population": 17.5, "gdp_share": 25.0, "electricity": 55.0, "poverty": 35.0},
            "Haut-Katanga": {"population": 4.5, "gdp_share": 18.0, "electricity": 30.0, "poverty": 45.0},
            "Kongo Central": {"population": 6.0, "gdp_share": 10.0, "electricity": 22.0, "poverty": 55.0},
            "Nord-Kivu": {"population": 8.5, "gdp_share": 8.0, "electricity": 12.0, "poverty": 72.0},
            "Sud-Kivu": {"population": 6.5, "gdp_share": 5.0, "electricity": 8.0, "poverty": 78.0},
            "Kasaï": {"population": 5.0, "gdp_share": 3.0, "electricity": 5.0, "poverty": 80.0},
            "Équateur": {"population": 3.5, "gdp_share": 2.5, "electricity": 7.0, "poverty": 70.0},
            "Tshopo": {"population": 3.0, "gdp_share": 4.0, "electricity": 10.0, "poverty": 65.0},
        }

    def get_budget_data(self) -> BudgetData:
        if not self.budget:
            self.load_drc_baseline()
        return self.budget  # type: ignore

    def get_economic_data(self) -> EconomicData:
        if not self.economy:
            self.load_drc_baseline()
        return self.economy  # type: ignore

    def get_social_data(self) -> SocialData:
        if not self.social:
            self.load_drc_baseline()
        return self.social  # type: ignore

    def get_all(self) -> dict:
        return {
            "budget": self.get_budget_data().to_dict(),
            "economy": self.get_economic_data().to_dict(),
            "social": self.get_social_data().to_dict(),
            "provinces": self.province_data,
        }

    def get_historical(self, years: int = 5) -> list[dict]:
        """Simule des données historiques."""
        current_year = 2024
        history = []
        for y in range(current_year - years + 1, current_year + 1):
            factor = 1.0 + (y - (current_year - years)) * 0.03
            history.append({
                "year": y,
                "gdp": round(55_000 * factor, 0),
                "revenue": round(12_500 * factor, 0),
                "expenditure": round(14_000 * factor, 0),
                "poverty_rate": round(max(50, 62 - (y - 2020) * 1.5), 1),
                "inflation": round(max(5, 12.5 - (y - 2020) * 1.0), 1),
                "electricity_access": round(min(50, 19 + (y - 2020) * 2.5), 1),
            })
        return history
