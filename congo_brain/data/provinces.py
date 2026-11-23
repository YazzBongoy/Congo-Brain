"""Référentiel administratif provincial de la RDC.

Découpage officiel en vigueur depuis 2015 : 26 provinces (Constitution du
18 février 2006, art. 2 ; loi de découpage territorial 2015). Inclut le
rattachement aux 11 provinces historiques (période 1988-2015) pour les
séries statistiques anciennes.

Sources : Ministère de l'Intérieur RDC (interieur.gouv.cd), INS RDC,
Banque Mondiale — estimations 2024-2026.
"""

from typing import Any

CURRENT_PROVINCE_COUNT = 26

PROVINCES_DRC: list[dict[str, Any]] = [
    {"name": "Kinshasa", "chef_lieu": "Kinshasa", "historical_province": "Kinshasa",
     "population": 17.0, "gdp": 13750, "poverty_rate": 35, "electricity_access": 55,
     "water_access": 70, "governance_score": 50, "area_km2": 9965, "literacy_rate": 85,
     "internet_access": 32, "security_index": 55},
    {"name": "Kongo Central", "chef_lieu": "Matadi", "historical_province": "Bas-Congo",
     "population": 6.8, "gdp": 5500, "poverty_rate": 55, "electricity_access": 22,
     "water_access": 40, "governance_score": 38, "area_km2": 53920, "literacy_rate": 68,
     "internet_access": 12, "security_index": 52},
    {"name": "Kwango", "chef_lieu": "Kenge", "historical_province": "Bandundu",
     "population": 2.8, "gdp": 850, "poverty_rate": 72, "electricity_access": 6,
     "water_access": 24, "governance_score": 32, "area_km2": 51640, "literacy_rate": 56,
     "internet_access": 5, "security_index": 58},
    {"name": "Kwilu", "chef_lieu": "Bandundu", "historical_province": "Bandundu",
     "population": 6.7, "gdp": 1750, "poverty_rate": 74, "electricity_access": 8,
     "water_access": 27, "governance_score": 33, "area_km2": 78442, "literacy_rate": 60,
     "internet_access": 7, "security_index": 57},
    {"name": "Mai-Ndombe", "chef_lieu": "Inongo", "historical_province": "Bandundu",
     "population": 2.5, "gdp": 750, "poverty_rate": 76, "electricity_access": 5,
     "water_access": 23, "governance_score": 30, "area_km2": 127465, "literacy_rate": 52,
     "internet_access": 4, "security_index": 54},
    {"name": "Kasaï", "chef_lieu": "Tshikapa", "historical_province": "Kasaï-Occidental",
     "population": 4.0, "gdp": 1100, "poverty_rate": 79, "electricity_access": 6,
     "water_access": 25, "governance_score": 30, "area_km2": 95631, "literacy_rate": 54,
     "internet_access": 5, "security_index": 53},
    {"name": "Kasaï-Central", "chef_lieu": "Kananga", "historical_province": "Kasaï-Occidental",
     "population": 5.9, "gdp": 1400, "poverty_rate": 77, "electricity_access": 9,
     "water_access": 28, "governance_score": 32, "area_km2": 59111, "literacy_rate": 58,
     "internet_access": 7, "security_index": 55},
    {"name": "Kasaï-Oriental", "chef_lieu": "Mbuji-Mayi", "historical_province": "Kasaï-Oriental",
     "population": 5.0, "gdp": 1650, "poverty_rate": 75, "electricity_access": 10,
     "water_access": 30, "governance_score": 34, "area_km2": 9481, "literacy_rate": 61,
     "internet_access": 8, "security_index": 55},
    {"name": "Lomami", "chef_lieu": "Kabinda", "historical_province": "Kasaï-Oriental",
     "population": 3.1, "gdp": 700, "poverty_rate": 78, "electricity_access": 5,
     "water_access": 22, "governance_score": 29, "area_km2": 56426, "literacy_rate": 51,
     "internet_access": 4, "security_index": 54},
    {"name": "Sankuru", "chef_lieu": "Lusambo", "historical_province": "Kasaï-Oriental",
     "population": 2.8, "gdp": 650, "poverty_rate": 80, "electricity_access": 4,
     "water_access": 21, "governance_score": 28, "area_km2": 105000, "literacy_rate": 49,
     "internet_access": 3, "security_index": 52},
    {"name": "Maniema", "chef_lieu": "Kindu", "historical_province": "Maniema",
     "population": 3.0, "gdp": 850, "poverty_rate": 73, "electricity_access": 8,
     "water_access": 26, "governance_score": 31, "area_km2": 132250, "literacy_rate": 55,
     "internet_access": 5, "security_index": 45},
    {"name": "Nord-Kivu", "chef_lieu": "Goma", "historical_province": "Nord-Kivu",
     "population": 8.5, "gdp": 4400, "poverty_rate": 72, "electricity_access": 12,
     "water_access": 30, "governance_score": 30, "area_km2": 59483, "literacy_rate": 66,
     "internet_access": 11, "security_index": 28},
    {"name": "Sud-Kivu", "chef_lieu": "Bukavu", "historical_province": "Sud-Kivu",
     "population": 8.0, "gdp": 3200, "poverty_rate": 74, "electricity_access": 11,
     "water_access": 29, "governance_score": 31, "area_km2": 65070, "literacy_rate": 64,
     "internet_access": 9, "security_index": 30},
    {"name": "Ituri", "chef_lieu": "Bunia", "historical_province": "Orientale",
     "population": 5.5, "gdp": 2400, "poverty_rate": 76, "electricity_access": 9,
     "water_access": 26, "governance_score": 29, "area_km2": 65658, "literacy_rate": 57,
     "internet_access": 6, "security_index": 26},
    {"name": "Haut-Uélé", "chef_lieu": "Isiro", "historical_province": "Orientale",
     "population": 2.4, "gdp": 600, "poverty_rate": 75, "electricity_access": 7,
     "water_access": 24, "governance_score": 30, "area_km2": 89683, "literacy_rate": 54,
     "internet_access": 5, "security_index": 44},
    {"name": "Bas-Uélé", "chef_lieu": "Buta", "historical_province": "Orientale",
     "population": 1.7, "gdp": 450, "poverty_rate": 77, "electricity_access": 5,
     "water_access": 22, "governance_score": 29, "area_km2": 148178, "literacy_rate": 50,
     "internet_access": 4, "security_index": 48},
    {"name": "Mongala", "chef_lieu": "Lisala", "historical_province": "Équateur",
     "population": 2.3, "gdp": 400, "poverty_rate": 78, "electricity_access": 5,
     "water_access": 23, "governance_score": 29, "area_km2": 58875, "literacy_rate": 51,
     "internet_access": 4, "security_index": 50},
    {"name": "Nord-Ubangi", "chef_lieu": "Gbadolite", "historical_province": "Équateur",
     "population": 2.1, "gdp": 380, "poverty_rate": 79, "electricity_access": 4,
     "water_access": 21, "governance_score": 28, "area_km2": 56644, "literacy_rate": 48,
     "internet_access": 3, "security_index": 47},
    {"name": "Sud-Ubangi", "chef_lieu": "Gemena", "historical_province": "Équateur",
     "population": 2.9, "gdp": 520, "poverty_rate": 77, "electricity_access": 5,
     "water_access": 23, "governance_score": 30, "area_km2": 51648, "literacy_rate": 50,
     "internet_access": 4, "security_index": 50},
    {"name": "Tshuapa", "chef_lieu": "Boende", "historical_province": "Équateur",
     "population": 2.0, "gdp": 350, "poverty_rate": 81, "electricity_access": 3,
     "water_access": 19, "governance_score": 27, "area_km2": 132941, "literacy_rate": 46,
     "internet_access": 3, "security_index": 49},
    {"name": "Tshopo", "chef_lieu": "Kisangani", "historical_province": "Orientale",
     "population": 4.2, "gdp": 1500, "poverty_rate": 72, "electricity_access": 13,
     "water_access": 31, "governance_score": 32, "area_km2": 199567, "literacy_rate": 62,
     "internet_access": 8, "security_index": 42},
    {"name": "Équateur", "chef_lieu": "Mbandaka", "historical_province": "Équateur",
     "population": 2.6, "gdp": 550, "poverty_rate": 79, "electricity_access": 5,
     "water_access": 22, "governance_score": 29, "area_km2": 131930, "literacy_rate": 49,
     "internet_access": 4, "security_index": 43},
    {"name": "Haut-Katanga", "chef_lieu": "Lubumbashi", "historical_province": "Katanga",
     "population": 6.2, "gdp": 9900, "poverty_rate": 48, "electricity_access": 30,
     "water_access": 45, "governance_score": 45, "area_km2": 132463, "literacy_rate": 72,
     "internet_access": 15, "security_index": 58},
    {"name": "Haut-Lomami", "chef_lieu": "Kamina", "historical_province": "Katanga",
     "population": 3.4, "gdp": 900, "poverty_rate": 71, "electricity_access": 7,
     "water_access": 25, "governance_score": 30, "area_km2": 108204, "literacy_rate": 55,
     "internet_access": 5, "security_index": 55},
    {"name": "Lualaba", "chef_lieu": "Kolwezi", "historical_province": "Katanga",
     "population": 3.5, "gdp": 6500, "poverty_rate": 62, "electricity_access": 18,
     "water_access": 32, "governance_score": 36, "area_km2": 121306, "literacy_rate": 60,
     "internet_access": 9, "security_index": 56},
    {"name": "Tanganyika", "chef_lieu": "Kalemie", "historical_province": "Katanga",
     "population": 3.6, "gdp": 1200, "poverty_rate": 73, "electricity_access": 8,
     "water_access": 25, "governance_score": 30, "area_km2": 134940, "literacy_rate": 54,
     "internet_access": 5, "security_index": 40},
]

_BASELINE_FIELDS = (
    "name", "population", "gdp", "poverty_rate", "electricity_access", "water_access",
    "governance_score", "area_km2", "literacy_rate", "internet_access", "security_index",
)

BASELINE_PROVINCES: list[dict[str, Any]] = [
    {k: p[k] for k in _BASELINE_FIELDS} for p in PROVINCES_DRC
]

HISTORICAL_PROVINCE_MAPPING: dict[str, list[str]] = {}
for _p in PROVINCES_DRC:
    HISTORICAL_PROVINCE_MAPPING.setdefault(_p["historical_province"], []).append(_p["name"])

assert len(PROVINCES_DRC) == CURRENT_PROVINCE_COUNT


_PRODUCTION_MINIERE = {
    "Lualaba": 9000, "Haut-Katanga": 6000, "Ituri": 1200, "Kasaï": 600,
    "Tanganyika": 800, "Sud-Kivu": 700, "Maniema": 500, "Tshopo": 400,
    "Kasaï-Oriental": 400, "Kongo Central": 250, "Nord-Kivu": 300,
    "Haut-Uélé": 150, "Lomami": 100, "Bas-Uélé": 120, "Sankuru": 150,
}


def _twin_fields(p: dict[str, Any]) -> dict[str, Any]:
    """Dérive les indicateurs infrastructure/économie du jumeau numérique."""
    pop, gdp, pov = p["population"], p["gdp"], p["poverty_rate"]
    return {
        "budget": max(200, round(gdp * 0.08)),
        "roads_km": round(1200 * pop ** 0.5 + p["area_km2"] / 80),
        "health_facilities": round(pop * 16),
        "schools": round(pop * 110),
        "enterprises": round(gdp * 9),
        "agricultural_output": round(pop * 85 * (1.2 - pov / 200)),
        "mining_output": _PRODUCTION_MINIERE.get(p["name"], 0),
        "life_expectancy": round(min(67, max(50, 66 - pov / 6))),
    }


TWIN_PROVINCES: list[dict[str, Any]] = [
    {**{k: v for k, v in BASELINE_PROVINCES[i].items() if k != "area_km2"}, **_twin_fields(p)}
    for i, p in enumerate(PROVINCES_DRC)
]
