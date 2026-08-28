"""Module 7: National Digital Twin — Jumeau numérique de la RDC.

Modélise chaque province et chaque secteur:
    Population, PIB, Budget, Routes, Santé, Éducation, Électricité, Entreprises

Permet de simuler des politiques publiques:
    "Que se passe-t-il si l'on investit 500M USD dans les routes du Kasaï?"
"""

from __future__ import annotations

from dataclasses import dataclass

from congo_brain.data.provinces import TWIN_PROVINCES


@dataclass
class ProvinceTwin:
    """Jumeau numérique d'une province."""

    name: str
    population: float = 0.0  # Millions
    gdp: float = 0.0  # M USD
    budget: float = 0.0  # M USD
    # Infrastructure
    roads_km: float = 0.0
    health_facilities: int = 0
    schools: int = 0
    electricity_access: float = 0.0  # %
    water_access: float = 0.0  # %
    internet_access: float = 0.0  # %
    # Économie
    enterprises: int = 0
    agricultural_output: float = 0.0  # M USD
    mining_output: float = 0.0  # M USD
    # Social
    poverty_rate: float = 0.0  # %
    literacy_rate: float = 0.0  # %
    life_expectancy: float = 0.0
    # État
    security_index: float = 0.0  # 0-100
    governance_score: float = 0.0  # 0-100

    @property
    def gdp_per_capita(self) -> float:
        return round(self.gdp / self.population, 0) if self.population > 0 else 0

    @property
    def budget_per_capita(self) -> float:
        return round(self.budget / self.population, 0) if self.population > 0 else 0

    @property
    def infrastructure_index(self) -> float:
        """Indice d'infrastructure composite (0-100)."""
        return round(
            self.electricity_access * 0.3
            + self.water_access * 0.2
            + self.internet_access * 0.2
            + min(100, self.health_facilities / self.population * 10) * 0.15
            + min(100, self.schools / self.population * 10) * 0.15,
            1,
        )

    @property
    def development_index(self) -> float:
        """Indice de développement composite (0-100)."""
        return round(
            (100 - self.poverty_rate) * 0.3
            + self.literacy_rate * 0.2
            + self.infrastructure_index * 0.25
            + self.governance_score * 0.15
            + self.security_index * 0.10,
            1,
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "population": round(self.population, 2),
            "gdp": round(self.gdp, 0),
            "budget": round(self.budget, 0),
            "gdp_per_capita": self.gdp_per_capita,
            "infrastructure_index": self.infrastructure_index,
            "development_index": self.development_index,
            "electricity_access": self.electricity_access,
            "water_access": self.water_access,
            "internet_access": self.internet_access,
            "poverty_rate": self.poverty_rate,
            "literacy_rate": self.literacy_rate,
            "health_facilities": self.health_facilities,
            "schools": self.schools,
            "enterprises": self.enterprises,
            "security_index": self.security_index,
            "governance_score": self.governance_score,
        }


# Provinces de la RDC — jumeau numérique
DRC_PROVINCES: list[dict] = TWIN_PROVINCES


class NationalDigitalTwin:
    """Jumeau numérique de la RDC.

    Modélise chaque province et permet la simulation
    de politiques publiques.
    """

    def __init__(self) -> None:
        self.provinces: dict[str, ProvinceTwin] = {}

    def load_baseline(self) -> None:
        for data in DRC_PROVINCES:
            pt = ProvinceTwin(**data)
            self.provinces[pt.name] = pt

    def add_province(self, province: ProvinceTwin) -> None:
        self.provinces[province.name] = province

    @property
    def total_population(self) -> float:
        return sum(p.population for p in self.provinces.values())

    @property
    def total_gdp(self) -> float:
        return sum(p.gdp for p in self.provinces.values())

    @property
    def total_budget(self) -> float:
        return sum(p.budget for p in self.provinces.values())

    @property
    def national_poverty_rate(self) -> float:
        weighted = sum(p.poverty_rate * p.population for p in self.provinces.values())
        return round(weighted / self.total_population, 1) if self.total_population > 0 else 0

    @property
    def national_electricity(self) -> float:
        weighted = sum(p.electricity_access * p.population for p in self.provinces.values())
        return round(weighted / self.total_population, 1) if self.total_population > 0 else 0

    def simulate_investment(self, province_name: str, sector: str, amount: float) -> dict:
        """Simule l'impact d'un investissement dans une province."""
        if province_name not in self.provinces:
            return {"error": f"Province {province_name} non trouvée"}

        p = self.provinces[province_name]

        # Estimation des impacts selon le secteur
        impacts = {
            "infrastructure": {
                "gdp_multiplier": 1.5,
                "poverty_reduction": amount / p.gdp * 2 if p.gdp > 0 else 0,
                "electricity_gain": amount / 1000 * 5,
            },
            "santé": {
                "gdp_multiplier": 0.8,
                "poverty_reduction": amount / p.gdp * 1.5 if p.gdp > 0 else 0,
                "life_expectancy_gain": amount / 500,
            },
            "éducation": {
                "gdp_multiplier": 1.2,
                "poverty_reduction": amount / p.gdp * 1.0 if p.gdp > 0 else 0,
                "literacy_gain": amount / 800,
            },
            "énergie": {
                "gdp_multiplier": 2.0,
                "poverty_reduction": amount / p.gdp * 3.0 if p.gdp > 0 else 0,
                "electricity_gain": amount / 200,
            },
            "agriculture": {
                "gdp_multiplier": 1.8,
                "poverty_reduction": amount / p.gdp * 2.5 if p.gdp > 0 else 0,
                "electricity_gain": 0,
            },
        }

        impact = impacts.get(sector, impacts["infrastructure"])

        return {
            "province": province_name,
            "sector": sector,
            "investment": amount,
            "expected_gdp_impact": round(amount * impact["gdp_multiplier"], 0),
            "poverty_reduction_pct": round(impact["poverty_reduction"], 1),
            "electricity_gain_pct": round(impact["electricity_gain"], 1),
            "new_development_index": round(min(100, p.development_index + impact["poverty_reduction"] * 2), 1),
        }

    def compare_provinces(self, top_n: int = 5) -> list[dict]:
        """Compare les provinces par indice de développement."""
        ranked = sorted(self.provinces.values(), key=lambda p: p.development_index, reverse=True)
        return [p.to_dict() for p in ranked[:top_n]]

    def get_dashboard(self) -> dict:
        return {
            "model": "NationalDigitalTwin",
            "total_population": round(self.total_population, 2),
            "total_gdp": round(self.total_gdp, 0),
            "total_budget": round(self.total_budget, 0),
            "national_poverty_rate": self.national_poverty_rate,
            "national_electricity_access": self.national_electricity,
            "province_count": len(self.provinces),
            "provinces": sorted(
                [p.to_dict() for p in self.provinces.values()], key=lambda x: x["development_index"], reverse=True
            ),
        }
