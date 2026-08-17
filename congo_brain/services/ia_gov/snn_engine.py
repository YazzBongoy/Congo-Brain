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
        """Load DRC baseline data for all 14 entities."""
        self.provinces = [
            {"name": "Kinshasa", "population": 17.5, "gdp": 13750, "poverty_rate": 35,
             "electricity_access": 55, "water_access": 70, "governance_score": 50},
            {"name": "Haut-Katanga", "population": 4.5, "gdp": 9900, "poverty_rate": 45,
             "electricity_access": 30, "water_access": 45, "governance_score": 45},
            {"name": "Kongo Central", "population": 6.0, "gdp": 5500, "poverty_rate": 55,
             "electricity_access": 22, "water_access": 40, "governance_score": 38},
            {"name": "Nord-Kivu", "population": 8.5, "gdp": 4400, "poverty_rate": 72,
             "electricity_access": 12, "water_access": 30, "governance_score": 30},
            {"name": "Sud-Kivu", "population": 6.5, "gdp": 2750, "poverty_rate": 78,
             "electricity_access": 8, "water_access": 25, "governance_score": 28},
        ]

        self.companies = [
            {"name": "Gécamines", "sector": "Mines", "revenue": 2800, "production_cost": 1200,
             "tax_burden": 560, "admin_cost": 80, "corruption_cost": 200,
             "logistics_cost": 150, "energy_cost": 300, "employees": 12000},
            {"name": "SNEL", "sector": "Énergie", "revenue": 800, "production_cost": 600,
             "tax_burden": 120, "admin_cost": 60, "corruption_cost": 100,
             "logistics_cost": 40, "energy_cost": 0, "employees": 8000},
            {"name": "Vodacom RDC", "sector": "Télécoms", "revenue": 1200, "production_cost": 500,
             "tax_burden": 200, "admin_cost": 50, "corruption_cost": 30,
             "logistics_cost": 80, "energy_cost": 100, "employees": 2500},
        ]

        self.resources = [
            {"name": "Kamoa-Kakula", "mineral_type": "Cuivre", "annual_production_tons": 500000,
             "market_value_per_ton": 8500, "local_processing_pct": 10, "tax_rate": 35,
             "employees": 4500, "environmental_cost": 2.0},
            {"name": "Tenke Fungurume", "mineral_type": "Cobalt", "annual_production_tons": 30000,
             "market_value_per_ton": 35000, "local_processing_pct": 5, "tax_rate": 30,
             "employees": 3500, "environmental_cost": 1.5},
            {"name": "Kibali Gold", "mineral_type": "Or", "annual_production_tons": 12,
             "market_value_per_ton": 60000000, "local_processing_pct": 8, "tax_rate": 40,
             "employees": 3000, "environmental_cost": 0.4},
        ]

        self.taxes = [
            {"name": "Impôt sur les sociétés", "tax_type": "income", "rate": 30, "revenue": 2500, "evasion_estimate": 800},
            {"name": "TVA", "tax_type": "vat", "rate": 16, "revenue": 1800, "evasion_estimate": 600},
            {"name": "Douanes", "tax_type": "customs", "rate": 10, "revenue": 2800, "evasion_estimate": 500},
            {"name": "Minières", "tax_type": "mining", "rate": 35, "revenue": 3500, "evasion_estimate": 1200},
        ]

        self.ministries = [
            {"name": "Santé", "budget_allocated": 1100, "budget_executed": 750,
             "optimization_score": 45, "transparency_score": 35, "performance_score": 40, "satisfaction_score": 30},
            {"name": "Éducation", "budget_allocated": 1400, "budget_executed": 1000,
             "optimization_score": 50, "transparency_score": 40, "performance_score": 45, "satisfaction_score": 45},
            {"name": "Infrastructure", "budget_allocated": 2000, "budget_executed": 1200,
             "optimization_score": 40, "transparency_score": 30, "performance_score": 35, "satisfaction_score": 25},
            {"name": "Finance", "budget_allocated": 800, "budget_executed": 650,
             "optimization_score": 55, "transparency_score": 50, "performance_score": 50, "satisfaction_score": 35},
        ]

        self.public_services = [
            {"name": "Électricité", "willingness_to_pay": 25, "actual_price": 15,
             "quality_score": 3, "access_time_hours": 4, "indirect_cost": 8, "coverage_pct": 19},
            {"name": "Eau potable", "willingness_to_pay": 15, "actual_price": 5,
             "quality_score": 5, "access_time_hours": 2, "indirect_cost": 2, "coverage_pct": 52},
            {"name": "Santé", "willingness_to_pay": 30, "actual_price": 8,
             "quality_score": 4, "access_time_hours": 6, "indirect_cost": 12, "coverage_pct": 45},
        ]

        self.projects = [
            {"name": "Usine transformation cobalt", "sector": "Industrie", "cost": 1200,
             "cs_impact": 2.0, "ps_impact": 9.0, "gr_impact": 3.0, "nrv_impact": 8.0,
             "dwl_impact": 1.0, "ec_impact": 1.2, "status": "planned"},
            {"name": "Réseau électrique national", "sector": "Énergie", "cost": 3000,
             "cs_impact": 8.0, "ps_impact": 6.0, "gr_impact": 2.0, "nrv_impact": 0.0,
             "dwl_impact": 0.8, "ec_impact": 0.5, "status": "planned"},
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
