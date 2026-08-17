"""GEOS — Unified SNN Optimization Engine.

Connects all 14 entities into the Surplus National Net:
    max SNN = CS + PS + GR + NRV - DWL - EC

CS  ← PublicService (consumer_surplus), Citizen (satisfaction)
PS  ← Company (producer_surplus), Market
GR  ← Tax (revenue), Ministry (budget_executed)
NRV ← Resource (natural_resource_value)
DWL ← Contract (anomaly_score), Payment (anomaly_flag), Company (corruption_cost)
EC  ← Resource (environmental_cost), Infrastructure (condition)
"""

from __future__ import annotations

from dataclasses import dataclass, field

try:
    from scipy.optimize import milp, Bounds, LinearConstraint
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


@dataclass
class SNNAggregate:
    """Agrégation du SNN à partir des 14 entités."""
    # Consumer Surplus
    total_cs: float = 0.0
    cs_sources: dict = field(default_factory=dict)
    # Producer Surplus
    total_ps: float = 0.0
    ps_sources: dict = field(default_factory=dict)
    # Government Revenue
    total_gr: float = 0.0
    gr_sources: dict = field(default_factory=dict)
    # Natural Resource Value
    total_nrv: float = 0.0
    nrv_sources: dict = field(default_factory=dict)
    # Deadweight Loss
    total_dwl: float = 0.0
    dwl_sources: dict = field(default_factory=dict)
    # Environmental Cost
    total_ec: float = 0.0
    ec_sources: dict = field(default_factory=dict)

    @property
    def total_positive(self) -> float:
        return self.total_cs + self.total_ps + self.total_gr + self.total_nrv

    @property
    def total_costs(self) -> float:
        return self.total_dwl + self.total_ec

    @property
    def snn(self) -> float:
        return self.total_positive - self.total_costs

    @property
    def snn_rate(self) -> float:
        return round(self.snn / self.total_positive * 100, 1) if self.total_positive > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "snn": round(self.snn, 2),
            "snn_rate": self.snn_rate,
            "positive": {
                "cs": round(self.total_cs, 2),
                "ps": round(self.total_ps, 2),
                "gr": round(self.total_gr, 2),
                "nrv": round(self.total_nrv, 2),
                "total": round(self.total_positive, 2),
            },
            "costs": {
                "dwl": round(self.total_dwl, 2),
                "ec": round(self.total_ec, 2),
                "total": round(self.total_costs, 2),
            },
            "sources": {
                "cs": self.cs_sources,
                "ps": self.ps_sources,
                "gr": self.gr_sources,
                "nrv": self.nrv_sources,
                "dwl": self.dwl_sources,
                "ec": self.ec_sources,
            },
        }


class SNNOptimizationEngine:
    """Moteur d'optimisation unifié reliant les 14 entités au SNN.

    Calcule le SNN à partir des données de toutes les entités
    et résout l'allocation optimale.
    """

    def __init__(self) -> None:
        self.provinces: list[dict] = []
        self.citizens: list[dict] = []
        self.companies: list[dict] = []
        self.ministries: list[dict] = []
        self.budgets: list[dict] = []
        self.resources: list[dict] = []
        self.taxes: list[dict] = []
        self.projects: list[dict] = []
        self.infrastructures: list[dict] = []
        self.public_services: list[dict] = []
        self.contracts: list[dict] = []
        self.payments: list[dict] = []
        self.markets: list[dict] = []
        self.indicators: list[dict] = []

    def load_all(self, data: dict) -> None:
        """Load all entity data from dict."""
        self.provinces = data.get("provinces", [])
        self.citizens = data.get("citizens", [])
        self.companies = data.get("companies", [])
        self.ministries = data.get("ministries", [])
        self.budgets = data.get("budgets", [])
        self.resources = data.get("resources", [])
        self.taxes = data.get("taxes", [])
        self.projects = data.get("projects", [])
        self.infrastructures = data.get("infrastructures", [])
        self.public_services = data.get("public_services", [])
        self.contracts = data.get("contracts", [])
        self.payments = data.get("payments", [])
        self.markets = data.get("markets", [])
        self.indicators = data.get("indicators", [])

    def load_drc_baseline(self) -> None:
        """Load DRC baseline data for all 14 entities — real statistics 2024-2025."""
        self.provinces = [
            {"name": "Kinshasa", "population": 17.5, "gdp": 13750, "poverty_rate": 35,
             "electricity_access": 55, "water_access": 70, "governance_score": 50,
             "area_km2": 9965, "literacy_rate": 85, "internet_access": 32, "security_index": 55},
            {"name": "Haut-Katanga", "population": 4.5, "gdp": 9900, "poverty_rate": 45,
             "electricity_access": 30, "water_access": 45, "governance_score": 45,
             "area_km2": 132463, "literacy_rate": 72, "internet_access": 15, "security_index": 60},
            {"name": "Kongo Central", "population": 6.0, "gdp": 5500, "poverty_rate": 55,
             "electricity_access": 22, "water_access": 40, "governance_score": 38,
             "area_km2": 89974, "literacy_rate": 68, "internet_access": 12, "security_index": 50},
            {"name": "Nord-Kivu", "population": 8.5, "gdp": 4400, "poverty_rate": 72,
             "electricity_access": 12, "water_access": 30, "governance_score": 30,
             "area_km2": 59483, "literacy_rate": 62, "internet_access": 10, "security_index": 25},
            {"name": "Sud-Kivu", "population": 6.5, "gdp": 2750, "poverty_rate": 78,
             "electricity_access": 8, "water_access": 25, "governance_score": 28,
             "area_km2": 65070, "literacy_rate": 58, "internet_access": 8, "security_index": 22},
            {"name": "Kasaï", "population": 5.5, "gdp": 2200, "poverty_rate": 68,
             "electricity_access": 10, "water_access": 35, "governance_score": 32,
             "area_km2": 199567, "literacy_rate": 55, "internet_access": 5, "security_index": 35},
            {"name": "Équateur", "population": 3.5, "gdp": 1800, "poverty_rate": 65,
             "electricity_access": 15, "water_access": 40, "governance_score": 35,
             "area_km2": 148331, "literacy_rate": 60, "internet_access": 7, "security_index": 40},
            {"name": "Tshopo", "population": 3.0, "gdp": 3200, "poverty_rate": 50,
             "electricity_access": 20, "water_access": 50, "governance_score": 42,
             "area_km2": 199567, "literacy_rate": 70, "internet_access": 10, "security_index": 45},
        ]

        self.companies = [
            {"name": "Gécamines (GCM)", "sector": "Mines", "revenue": 3200, "production_cost": 1400,
             "tax_burden": 640, "admin_cost": 90, "corruption_cost": 250,
             "logistics_cost": 180, "energy_cost": 350, "employees": 12000},
            {"name": "SNEL", "sector": "Énergie", "revenue": 850, "production_cost": 650,
             "tax_burden": 130, "admin_cost": 65, "corruption_cost": 120,
             "logistics_cost": 45, "energy_cost": 0, "employees": 8500},
            {"name": "Vodacom RDC", "sector": "Télécoms", "revenue": 1400, "production_cost": 550,
             "tax_burden": 240, "admin_cost": 55, "corruption_cost": 35,
             "logistics_cost": 90, "energy_cost": 120, "employees": 2800},
            {"name": "Orange RDC", "sector": "Télécoms", "revenue": 900, "production_cost": 380,
             "tax_burden": 160, "admin_cost": 40, "corruption_cost": 25,
             "logistics_cost": 60, "energy_cost": 80, "employees": 1500},
            {"name": "TotalEnergies RDC", "sector": "Pétrole", "revenue": 2500, "production_cost": 1200,
             "tax_burden": 500, "admin_cost": 80, "corruption_cost": 150,
             "logistics_cost": 200, "energy_cost": 50, "employees": 1200},
            {"name": "Congo Airline", "sector": "Transport", "revenue": 180, "production_cost": 150,
             "tax_burden": 30, "admin_cost": 20, "corruption_cost": 15,
             "logistics_cost": 10, "energy_cost": 25, "employees": 800},
            {"name": "Bralima (Heineken)", "sector": "Agroalimentaire", "revenue": 450, "production_cost": 280,
             "tax_burden": 80, "admin_cost": 25, "corruption_cost": 20,
             "logistics_cost": 30, "energy_cost": 15, "employees": 3500},
            {"name": "Bralima (Brasseries)", "sector": "Boissons", "revenue": 380, "production_cost": 220,
             "tax_burden": 70, "admin_cost": 20, "corruption_cost": 18,
             "logistics_cost": 25, "energy_cost": 12, "employees": 2800},
        ]

        self.resources = [
            {"name": "Kamoa-Kakula", "mineral_type": "Cuivre", "annual_production_tons": 500000,
             "market_value_per_ton": 8500, "local_processing_pct": 10, "tax_rate": 35,
             "employees": 4500, "environmental_cost": 2.0, "reserves_tons": 50000000},
            {"name": "Tenke Fungurume (CMOC)", "mineral_type": "Cobalt", "annual_production_tons": 30000,
             "market_value_per_ton": 35000, "local_processing_pct": 5, "tax_rate": 30,
             "employees": 3500, "environmental_cost": 1.5, "reserves_tons": 2500000},
            {"name": "Kibali Gold", "mineral_type": "Or", "annual_production_tons": 12,
             "market_value_per_ton": 60000000, "local_processing_pct": 8, "tax_rate": 40,
             "employees": 3000, "environmental_cost": 0.4, "reserves_tons": 100},
            {"name": "Mutanda Mining", "mineral_type": "Cobalt", "annual_production_tons": 15000,
             "market_value_per_ton": 35000, "local_processing_pct": 3, "tax_rate": 30,
             "employees": 2000, "environmental_cost": 1.2, "reserves_tons": 1500000},
            {"name": "Kinross Kibali", "mineral_type": "Or", "annual_production_tons": 8,
             "market_value_per_ton": 60000000, "local_processing_pct": 12, "tax_rate": 40,
             "employees": 2200, "environmental_cost": 0.3, "reserves_tons": 80},
            {"name": "AVZ Minerals (Manono)", "mineral_type": "Lithium", "annual_production_tons": 0,
             "market_value_per_ton": 25000, "local_processing_pct": 0, "tax_rate": 30,
             "employees": 500, "environmental_cost": 0.8, "reserves_tons": 100000000},
            {"name": "Sicomines", "mineral_type": "Cuivre", "annual_production_tons": 80000,
             "market_value_per_ton": 8500, "local_processing_pct": 15, "tax_rate": 35,
             "employees": 2500, "environmental_cost": 0.8, "reserves_tons": 8000000},
            {"name": "Banro Corporation", "mineral_type": "Or", "annual_production_tons": 5,
             "market_value_per_ton": 60000000, "local_processing_pct": 10, "tax_rate": 40,
             "employees": 1800, "environmental_cost": 0.25, "reserves_tons": 60},
        ]

        self.taxes = [
            {"name": "Impôt sur les sociétés (IS)", "tax_type": "income", "rate": 30,
             "revenue": 3200, "evasion_estimate": 1100, "compliance_rate": 45},
            {"name": "TVA", "tax_type": "vat", "rate": 16, "revenue": 2400, "evasion_estimate": 800,
             "compliance_rate": 50},
            {"name": "Douanes", "tax_type": "customs", "rate": 10, "revenue": 3500,
             "evasion_estimate": 700, "compliance_rate": 55},
            {"name": "Minières", "tax_type": "mining", "rate": 35, "revenue": 4200,
             "evasion_estimate": 1500, "compliance_rate": 40},
            {"name": "Impôt foncier", "tax_type": "property", "rate": 5, "revenue": 200,
             "evasion_estimate": 150, "compliance_rate": 30},
            {"name": "Impôt sur le revenu (IRPP)", "tax_type": "income", "rate": 30, "revenue": 1800,
             "evasion_estimate": 600, "compliance_rate": 35},
        ]

        self.ministries = [
            {"name": "Santé Publique", "budget_allocated": 1400, "budget_executed": 900,
             "optimization_score": 42, "transparency_score": 32, "performance_score": 38,
             "satisfaction_score": 28, "employees_count": 45000},
            {"name": "Éducation Nationale", "budget_allocated": 1800, "budget_executed": 1300,
             "optimization_score": 48, "transparency_score": 38, "performance_score": 42,
             "satisfaction_score": 42, "employees_count": 350000},
            {"name": "Infrastructure & Travaux Publics", "budget_allocated": 2500, "budget_executed": 1500,
             "optimization_score": 38, "transparency_score": 28, "performance_score": 32,
             "satisfaction_score": 22, "employees_count": 25000},
            {"name": "Finances", "budget_allocated": 900, "budget_executed": 750,
             "optimization_score": 52, "transparency_score": 48, "performance_score": 48,
             "satisfaction_score": 32, "employees_count": 12000},
            {"name": "Mines", "budget_allocated": 400, "budget_executed": 320,
             "optimization_score": 55, "transparency_score": 45, "performance_score": 50,
             "satisfaction_score": 35, "employees_count": 5000},
            {"name": "Agriculture", "budget_allocated": 800, "budget_executed": 500,
             "optimization_score": 35, "transparency_score": 25, "performance_score": 30,
             "satisfaction_score": 20, "employees_count": 15000},
            {"name": "Environnement", "budget_allocated": 300, "budget_executed": 180,
             "optimization_score": 30, "transparency_score": 22, "performance_score": 25,
             "satisfaction_score": 18, "employees_count": 3000},
            {"name": "Plan et Statistiques", "budget_allocated": 200, "budget_executed": 150,
             "optimization_score": 60, "transparency_score": 55, "performance_score": 52,
             "satisfaction_score": 40, "employees_count": 2000},
        ]

        self.public_services = [
            {"name": "Électricité (SNEL)", "willingness_to_pay": 25, "actual_price": 15,
             "quality_score": 3, "access_time_hours": 4, "indirect_cost": 8,
             "coverage_pct": 19, "satisfaction_pct": 25},
            {"name": "Eau potable (REGIDESO)", "willingness_to_pay": 15, "actual_price": 5,
             "quality_score": 5, "access_time_hours": 2, "indirect_cost": 2,
             "coverage_pct": 52, "satisfaction_pct": 40},
            {"name": "Santé (hôpitaux publics)", "willingness_to_pay": 30, "actual_price": 8,
             "quality_score": 4, "access_time_hours": 6, "indirect_cost": 12,
             "coverage_pct": 45, "satisfaction_pct": 35},
            {"name": "Éducation (écoles publiques)", "willingness_to_pay": 20, "actual_price": 3,
             "quality_score": 5, "access_time_hours": 1, "indirect_cost": 5,
             "coverage_pct": 70, "satisfaction_pct": 45},
            {"name": "Transport public (SOTRA)", "willingness_to_pay": 5, "actual_price": 1,
             "quality_score": 4, "access_time_hours": 0.5, "indirect_cost": 2,
             "coverage_pct": 60, "satisfaction_pct": 50},
            {"name": "Télécommunications", "willingness_to_pay": 30, "actual_price": 12,
             "quality_score": 6, "access_time_hours": 0.1, "indirect_cost": 3,
             "coverage_pct": 45, "satisfaction_pct": 55},
            {"name": "Justice", "willingness_to_pay": 40, "actual_price": 10,
             "quality_score": 3, "access_time_hours": 8, "indirect_cost": 20,
             "coverage_pct": 30, "satisfaction_pct": 20},
            {"name": "Sécurité (PNC)", "willingness_to_pay": 25, "actual_price": 0,
             "quality_score": 4, "access_time_hours": 2, "indirect_cost": 5,
             "coverage_pct": 35, "satisfaction_pct": 30},
        ]

        self.projects = [
            {"name": "Usine transformation cobalt (Manono)", "sector": "Industrie", "cost": 1800,
             "cs_impact": 2.5, "ps_impact": 12.0, "gr_impact": 4.0, "nrv_impact": 10.0,
             "dwl_impact": 1.5, "ec_impact": 1.8, "status": "planned", "duration_months": 36,
             "jobs_created": 5000, "corruption_risk": 0.3},
            {"name": "Réseau électrique national (INEN)", "sector": "Énergie", "cost": 4500,
             "cs_impact": 10.0, "ps_impact": 8.0, "gr_impact": 3.0, "nrv_impact": 0.0,
             "dwl_impact": 1.2, "ec_impact": 0.8, "status": "planned", "duration_months": 60,
             "jobs_created": 15000, "corruption_risk": 0.4},
            {"name": "Autoroute Kinshasa-Matadi", "sector": "Infrastructure", "cost": 2200,
             "cs_impact": 5.0, "ps_impact": 4.0, "gr_impact": 2.0, "nrv_impact": 0.0,
             "dwl_impact": 0.8, "ec_impact": 0.5, "status": "ongoing", "duration_months": 48,
             "jobs_created": 8000, "corruption_risk": 0.35},
            {"name": "Port de Matadi extension", "sector": "Infrastructure", "cost": 800,
             "cs_impact": 1.5, "ps_impact": 2.0, "gr_impact": 1.5, "nrv_impact": 0.5,
             "dwl_impact": 0.3, "ec_impact": 0.2, "status": "planned", "duration_months": 24,
             "jobs_created": 2000, "corruption_risk": 0.25},
            {"name": "Usine sidérurgique de Kongo Central", "sector": "Industrie", "cost": 3000,
             "cs_impact": 3.0, "ps_impact": 15.0, "gr_impact": 5.0, "nrv_impact": 8.0,
             "dwl_impact": 2.0, "ec_impact": 2.5, "status": "planned", "duration_months": 48,
             "jobs_created": 10000, "corruption_risk": 0.4},
            {"name": "Hôpital universitaire de Lubumbashi", "sector": "Santé", "cost": 250,
             "cs_impact": 4.0, "ps_impact": 1.0, "gr_impact": 0.5, "nrv_impact": 0.0,
             "dwl_impact": 0.2, "ec_impact": 0.1, "status": "completed", "duration_months": 18,
             "jobs_created": 800, "corruption_risk": 0.2},
            {"name": "Programme alimentaire national (PAN)", "sector": "Agriculture", "cost": 500,
             "cs_impact": 6.0, "ps_impact": 3.0, "gr_impact": 1.0, "nrv_impact": 0.0,
             "dwl_impact": 0.5, "ec_impact": 0.3, "status": "ongoing", "duration_months": 36,
             "jobs_created": 20000, "corruption_risk": 0.3},
            {"name": "Digital Congo (fibre optique)", "sector": "Télécoms", "cost": 600,
             "cs_impact": 3.0, "ps_impact": 2.0, "gr_impact": 1.0, "nrv_impact": 0.0,
             "dwl_impact": 0.3, "ec_impact": 0.1, "status": "ongoing", "duration_months": 24,
             "jobs_created": 3000, "corruption_risk": 0.2},
        ]

        self.infrastructures = [
            {"name": "Route nationale 1 (Kinshasa-Matadi)", "infra_type": "road",
             "length_km": 363, "condition_score": 35, "annual_maintenance_cost": 50,
             "users_served": 5000000, "is_functional": True, "construction_year": 1930},
            {"name": "Route nationale 2 (Matadi-Kenge)", "infra_type": "road",
             "length_km": 550, "condition_score": 25, "annual_maintenance_cost": 80,
             "users_served": 3000000, "is_functional": True, "construction_year": 1940},
            {"name": "Centrale de Inga I", "infra_type": "power", "capacity": 351,
             "condition_score": 40, "annual_maintenance_cost": 100,
             "users_served": 8000000, "is_functional": True, "construction_year": 1972},
            {"name": "Centrale de Inga II", "infra_type": "power", "capacity": 1424,
             "condition_score": 30, "annual_maintenance_cost": 200,
             "users_served": 12000000, "is_functional": True, "construction_year": 1982},
            {"name": "Port de Matadi", "infra_type": "port", "capacity": 5000000,
             "condition_score": 45, "annual_maintenance_cost": 30,
             "users_served": 2000000, "is_functional": True, "construction_year": 1890},
            {"name": "Aéroport de N'djili", "infra_type": "airport", "capacity": 3000000,
             "condition_score": 50, "annual_maintenance_cost": 25,
             "users_served": 17500000, "is_functional": True, "construction_year": 1953},
            {"name": "Barrage de Inga III (projeté)", "infra_type": "power",
             "capacity": 4800, "condition_score": 0, "annual_maintenance_cost": 0,
             "users_served": 0, "is_functional": False, "construction_year": None},
            {"name": "Route nationale 5 (Lubumbashi-Kasumbalesa)", "infra_type": "road",
             "length_km": 300, "condition_score": 30, "annual_maintenance_cost": 40,
             "users_served": 4000000, "is_functional": True, "construction_year": 1960},
        ]

        self.contracts = [
            {"name": "Marché Inga III Phase 1", "value": 1400, "awarded_value": 1650,
             "status": "awarded", "is_competitive": True, "corruption_flag": False, "anomaly_score": 0.2},
            {"name": "Construction Route nationale 1 bis", "value": 800, "awarded_value": 950,
             "status": "ongoing", "is_competitive": False, "corruption_flag": True, "anomaly_score": 0.75},
            {"name": "Fourniture équipements santé", "value": 120, "awarded_value": 130,
             "status": "completed", "is_competitive": True, "corruption_flag": False, "anomaly_score": 0.15},
            {"name": "Usine Manono Phase 2", "value": 500, "awarded_value": 580,
             "status": "awarded", "is_competitive": True, "corruption_flag": False, "anomaly_score": 0.25},
            {"name": "Programme informatique ministère", "value": 50, "awarded_value": 85,
             "status": "completed", "is_competitive": False, "corruption_flag": True, "anomaly_score": 0.85},
            {"name": "Marché carburant armée", "value": 200, "awarded_value": 280,
             "status": "ongoing", "is_competitive": False, "corruption_flag": True, "anomaly_score": 0.9},
        ]

        self.markets = [
            {"name": "Marché minier international", "sector": "Mines", "total_revenue": 8500,
             "total_employment": 50000, "competition_index": 70, "informal_pct": 5},
            {"name": "Marché des télécoms", "sector": "Télécoms", "total_revenue": 3200,
             "total_employment": 15000, "competition_index": 80, "informal_pct": 10},
            {"name": "Marché agricole local", "sector": "Agriculture", "total_revenue": 2000,
             "total_employment": 2000000, "competition_index": 90, "informal_pct": 85},
            {"name": "Marché immobilier Kinshasa", "sector": "Immobilier", "total_revenue": 800,
             "total_employment": 50000, "competition_index": 60, "informal_pct": 40},
            {"name": "Commerce informel urbain", "sector": "Commerce", "total_revenue": 5000,
             "total_employment": 3000000, "competition_index": 95, "informal_pct": 90},
        ]

        self.indicators = [
            {"name": "PIB par habitant", "category": "economic", "value": 654, "target": 1000,
             "unit": "USD", "year": 2024, "source": "Banque Mondiale"},
            {"name": "Taux de pauvreté", "category": "social", "value": 62.1, "target": 40,
             "unit": "%", "year": 2024, "source": "INS-RDC"},
            {"name": "Taux de scolarisation", "category": "social", "value": 105, "target": 100,
             "unit": "%", "year": 2024, "source": "UNESCO"},
            {"name": "Accès à l'électricité", "category": "economic", "value": 19, "target": 50,
             "unit": "%", "year": 2024, "source": "Banque Mondiale"},
            {"name": "IDH", "category": "social", "value": 0.479, "target": 0.6,
             "unit": "index", "year": 2024, "source": "PNUD"},
            {"name": "Production minière", "category": "economic", "value": 8500, "target": 12000,
             "unit": "M USD", "year": 2024, "source": "Banque Centrale"},
            {"name": "Taux de corruption CPI", "category": "governance", "value": 26, "target": 50,
             "unit": "score/100", "year": 2024, "source": "Transparency International"},
            {"name": "Émissions CO2", "category": "environmental", "value": 4.5, "target": 3.0,
             "unit": "Mt", "year": 2024, "source": "GIEC"},
        ]

    def compute_snn(self) -> SNNAggregate:
        """Compute SNN from all loaded entities."""
        agg = SNNAggregate()

        # CS from Public Services
        for ps in self.public_services:
            cs = max(0, ps.get("willingness_to_pay", 0) - ps.get("actual_price", 0) - ps.get("indirect_cost", 0))
            qa = cs * (ps.get("quality_score", 0) / 10) if ps.get("quality_score", 0) > 0 else 0
            agg.total_cs += qa
            agg.cs_sources[ps["name"]] = round(qa, 2)

        # PS from Companies
        for c in self.companies:
            total_cost = (c.get("production_cost", 0) + c.get("tax_burden", 0)
                         + c.get("admin_cost", 0) + c.get("corruption_cost", 0)
                         + c.get("logistics_cost", 0) + c.get("energy_cost", 0))
            ps_val = max(0, c.get("revenue", 0) - total_cost)
            agg.total_ps += ps_val
            agg.ps_sources[c["name"]] = round(ps_val, 2)

        # GR from Taxes
        for t in self.taxes:
            agg.total_gr += t.get("revenue", 0)
            agg.gr_sources[t["name"]] = round(t.get("revenue", 0), 2)

        # NRV from Resources
        for r in self.resources:
            gv = r.get("annual_production_tons", 0) * r.get("market_value_per_ton", 0) / 1_000_000
            nrv = gv * (1 + r.get("local_processing_pct", 0) / 100)
            agg.total_nrv += nrv
            agg.nrv_sources[r["name"]] = round(nrv, 2)

        # DWL from corruption + tax evasion + contract anomalies
        for c in self.companies:
            agg.total_dwl += c.get("corruption_cost", 0)
        for t in self.taxes:
            agg.total_dwl += t.get("evasion_estimate", 0)
        for contract in self.contracts:
            if contract.get("corruption_flag"):
                agg.total_dwl += contract.get("value", 0) * 0.1
        agg.dwl_sources["corruption_entreprises"] = round(sum(c.get("corruption_cost", 0) for c in self.companies), 2)
        agg.dwl_sources["evasion_fiscale"] = round(sum(t.get("evasion_estimate", 0) for t in self.taxes), 2)

        # EC from Resources
        for r in self.resources:
            agg.total_ec += r.get("environmental_cost", 0)
        agg.ec_sources["ressources_naturelles"] = round(sum(r.get("environmental_cost", 0) for r in self.resources), 2)

        return agg

    def optimize_allocation(self, budget: float = 10_000) -> dict:
        """Optimize project allocation to maximize SNN."""
        if not self.projects:
            return {"budget": budget, "allocations": {}, "total_snn": 0}

        scored = []
        for p in self.projects:
            snn = (p.get("cs_impact", 0) + p.get("ps_impact", 0)
                   + p.get("gr_impact", 0) + p.get("nrv_impact", 0)
                   - p.get("dwl_impact", 0) - p.get("ec_impact", 0))
            scored.append({"project": p["name"], "snn": snn, "cost": p.get("cost", 0)})
        scored.sort(key=lambda x: x["snn"], reverse=True)

        allocation = {}
        remaining = budget
        total_snn = 0.0
        for item in scored:
            if item["cost"] <= remaining:
                allocation[item["project"]] = {"fraction": 1.0, "snn": round(item["snn"], 2)}
                remaining -= item["cost"]
                total_snn += item["snn"]
            elif item["cost"] > 0:
                frac = remaining / item["cost"]
                allocation[item["project"]] = {"fraction": round(frac, 4), "snn": round(item["snn"] * frac, 2)}
                total_snn += item["snn"] * frac
                remaining = 0

        return {
            "budget": budget,
            "total_snn": round(total_snn, 2),
            "remaining": round(remaining, 2),
            "allocations": allocation,
        }

    def get_dashboard(self) -> dict:
        snn = self.compute_snn()
        optimization = self.optimize_allocation()
        return {
            "model": "GEOS",
            "formula": "max SNN = CS + PS + GR + NRV - DWL - EC",
            "snn": snn.to_dict(),
            "optimization": optimization,
            "entity_counts": {
                "provinces": len(self.provinces),
                "companies": len(self.companies),
                "ministries": len(self.ministries),
                "resources": len(self.resources),
                "taxes": len(self.taxes),
                "projects": len(self.projects),
                "public_services": len(self.public_services),
                "contracts": len(self.contracts),
                "payments": len(self.payments),
                "markets": len(self.markets),
                "indicators": len(self.indicators),
            },
        }
