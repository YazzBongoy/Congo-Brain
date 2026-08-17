"""Tests for GEOS SNN Optimization Engine — 14 entities, SNN formula."""

import pytest
from congo_brain.services.ia_gov.snn_engine import SNNOptimizationEngine, SNNAggregate


class TestSNNAggregate:
    """Test SNNAggregate data class."""

    def test_empty_aggregate(self):
        agg = SNNAggregate()
        assert agg.snn == 0
        assert agg.total_positive == 0
        assert agg.total_costs == 0

    def test_snn_positive(self):
        agg = SNNAggregate(total_cs=10, total_ps=20, total_gr=15, total_nrv=5,
                           total_dwl=3, total_ec=2)
        assert agg.snn == 45
        assert agg.total_positive == 50
        assert agg.total_costs == 5

    def test_snn_rate(self):
        agg = SNNAggregate(total_cs=10, total_ps=20, total_gr=15, total_nrv=5,
                           total_dwl=3, total_ec=2)
        assert agg.snn_rate == 90.0

    def test_snn_rate_zero_positive(self):
        agg = SNNAggregate()
        assert agg.snn_rate == 0.0

    def test_to_dict_structure(self):
        agg = SNNAggregate(total_cs=10, total_ps=20, total_gr=15, total_nrv=5,
                           total_dwl=3, total_ec=2, cs_sources={"a": 10})
        d = agg.to_dict()
        assert "snn" in d
        assert "positive" in d
        assert "costs" in d
        assert "sources" in d
        assert d["positive"]["cs"] == 10
        assert d["costs"]["dwl"] == 3


class TestSNNOptimizationEngine:
    """Test SNNOptimizationEngine core logic."""

    def test_init(self):
        engine = SNNOptimizationEngine()
        assert engine.resources == []
        assert engine.companies == []

    def test_load_empty(self):
        engine = SNNOptimizationEngine()
        engine.load_all({})
        assert engine.resources == []

    def test_load_drc_baseline(self):
        engine = SNNOptimizationEngine()
        engine.load_drc_baseline()
        assert len(engine.provinces) == 5
        assert len(engine.companies) == 3
        assert len(engine.resources) == 3
        assert len(engine.taxes) == 4
        assert len(engine.ministries) == 4

    def test_compute_snn_empty(self):
        engine = SNNOptimizationEngine()
        agg = engine.compute_snn()
        assert agg.snn == 0

    def test_compute_snn_from_companies(self):
        engine = SNNOptimizationEngine()
        engine.companies = [
            {"name": "Test", "revenue": 100, "production_cost": 30,
             "tax_burden": 10, "admin_cost": 5, "corruption_cost": 5,
             "logistics_cost": 5, "energy_cost": 5}
        ]
        agg = engine.compute_snn()
        assert agg.ps_sources["Test"] == 40

    def test_compute_snn_from_resources(self):
        engine = SNNOptimizationEngine()
        engine.resources = [
            {"name": "Mine", "annual_production_tons": 1000,
             "market_value_per_ton": 10000, "local_processing_pct": 20,
             "tax_rate": 30, "environmental_cost": 1.5}
        ]
        agg = engine.compute_snn()
        assert agg.nrv_sources["Mine"] == 12.0  # 10*1.2
        assert agg.ec_sources["ressources_naturelles"] == 1.5

    def test_compute_snn_from_public_services(self):
        engine = SNNOptimizationEngine()
        engine.public_services = [
            {"name": "Santé", "willingness_to_pay": 30, "actual_price": 8,
             "quality_score": 4, "indirect_cost": 12}
        ]
        agg = engine.compute_snn()
        # CS = 30-8-12=10, QA = 10*0.4=4
        assert agg.cs_sources["Santé"] == 4.0

    def test_compute_snn_from_taxes(self):
        engine = SNNOptimizationEngine()
        engine.taxes = [
            {"name": "TVA", "revenue": 500, "evasion_estimate": 100}
        ]
        agg = engine.compute_snn()
        assert agg.gr_sources["TVA"] == 500
        assert agg.dwl_sources["evasion_fiscale"] == 100

    def test_compute_snn_from_corruption(self):
        engine = SNNOptimizationEngine()
        engine.companies = [
            {"name": "C1", "revenue": 0, "corruption_cost": 50}
        ]
        agg = engine.compute_snn()
        assert agg.dwl_sources["corruption_entreprises"] == 50

    def test_compute_snn_from_contracts(self):
        engine = SNNOptimizationEngine()
        engine.contracts = [
            {"name": "C1", "value": 100, "corruption_flag": True}
        ]
        agg = engine.compute_snn()
        assert agg.dwl_sources["corruption_entreprises"] == 0
        assert agg.total_dwl == 10.0  # 10% of 100

    def test_snn_formula_all_components(self):
        engine = SNNOptimizationEngine()
        engine.public_services = [{"name": "E", "willingness_to_pay": 10, "actual_price": 5,
                                   "quality_score": 10, "indirect_cost": 0}]  # CS=5
        engine.companies = [{"name": "C", "revenue": 100, "production_cost": 20,
                             "tax_burden": 10, "admin_cost": 5, "corruption_cost": 15,
                             "logistics_cost": 5, "energy_cost": 5}]  # PS=40
        engine.taxes = [{"name": "T", "revenue": 80, "evasion_estimate": 10}]  # GR=80, DWL+=10
        engine.resources = [{"name": "R", "annual_production_tons": 100,
                             "market_value_per_ton": 10000, "local_processing_pct": 0,
                             "tax_rate": 0, "environmental_cost": 5}]  # NRV=1, EC=5
        agg = engine.compute_snn()
        # SNN = 5 + 40 + 80 + 1 - (0 + 15 + 10) - 5 = 96
        assert agg.snn == 96.0

    def test_optimize_allocation_empty(self):
        engine = SNNOptimizationEngine()
        result = engine.optimize_allocation(1000)
        assert result["total_snn"] == 0

    def test_optimize_allocation_single_project(self):
        engine = SNNOptimizationEngine()
        engine.projects = [{"name": "P1", "cost": 500, "cs_impact": 10,
                            "ps_impact": 20, "gr_impact": 5, "nrv_impact": 0,
                            "dwl_impact": 2, "ec_impact": 1}]
        result = engine.optimize_allocation(1000)
        assert result["total_snn"] == 32.0

    def test_optimize_allocation_budget_constraint(self):
        engine = SNNOptimizationEngine()
        engine.projects = [
            {"name": "P1", "cost": 800, "cs_impact": 10, "ps_impact": 20,
             "gr_impact": 5, "nrv_impact": 0, "dwl_impact": 2, "ec_impact": 1},
            {"name": "P2", "cost": 800, "cs_impact": 5, "ps_impact": 5,
             "gr_impact": 5, "nrv_impact": 0, "dwl_impact": 1, "ec_impact": 1},
        ]
        result = engine.optimize_allocation(1000)
        assert "P1" in result["allocations"]
        assert result["allocations"]["P1"]["fraction"] == 1.0
        assert result["remaining"] == 0.0  # P2 fractional consumed remaining

    def test_optimize_allocation_fractional(self):
        engine = SNNOptimizationEngine()
        engine.projects = [
            {"name": "P1", "cost": 500, "cs_impact": 10, "ps_impact": 10,
             "gr_impact": 0, "nrv_impact": 0, "dwl_impact": 0, "ec_impact": 0}
        ]
        result = engine.optimize_allocation(250)
        assert result["allocations"]["P1"]["fraction"] == 0.5
        assert result["allocations"]["P1"]["snn"] == 10.0

    def test_get_dashboard(self):
        engine = SNNOptimizationEngine()
        engine.load_drc_baseline()
        d = engine.get_dashboard()
        assert d["model"] == "GEOS"
        assert "snn" in d
        assert "optimization" in d
        assert "entity_counts" in d
        assert d["entity_counts"]["provinces"] == 5


class TestGEOSAPI:
    """Test GEOS API endpoints."""

    def test_geos_dashboard(self, client):
        r = client.get("/api/v1/geos/dashboard")
        assert r.status_code == 200
        d = r.json()
        assert d["model"] == "GEOS"
        assert d["snn"]["snn"] > 0

    def test_geos_snn(self, client):
        r = client.get("/api/v1/geos/snn")
        assert r.status_code == 200
        d = r.json()
        assert "positive" in d
        assert "costs" in d

    def test_geos_optimize(self, client):
        r = client.post("/api/v1/geos/optimize", json={"budget": 5000})
        assert r.status_code == 200
        d = r.json()
        assert d["budget"] == 5000

    def test_geos_provinces(self, client):
        r = client.get("/api/v1/geos/provinces")
        assert r.status_code == 200
        assert len(r.json()) == 5

    def test_geos_provinces_kinshasa(self, client):
        r = client.get("/api/v1/geos/provinces/Kinshasa")
        assert r.status_code == 200
        assert r.json()["population"] == 17.5

    def test_geos_provinces_not_found(self, client):
        r = client.get("/api/v1/geos/provinces/Inexistante")
        assert r.status_code == 404

    def test_geos_companies(self, client):
        r = client.get("/api/v1/geos/companies")
        assert r.status_code == 200
        assert len(r.json()) == 3

    def test_geos_companies_ps_total(self, client):
        r = client.get("/api/v1/geos/companies/ps/total")
        assert r.status_code == 200
        d = r.json()
        assert d["total_ps"] > 0
        assert "Gécamines" in d["details"]

    def test_geos_ministries(self, client):
        r = client.get("/api/v1/geos/ministries")
        assert r.status_code == 200
        assert len(r.json()) == 4

    def test_geos_ministries_ranking(self, client):
        r = client.get("/api/v1/geos/ministries/ranking")
        assert r.status_code == 200
        ranking = r.json()
        assert ranking[0]["governance_score"] >= ranking[-1]["governance_score"]

    def test_geos_resources(self, client):
        r = client.get("/api/v1/geos/resources")
        assert r.status_code == 200
        assert len(r.json()) == 3

    def test_geos_resources_nrv_total(self, client):
        r = client.get("/api/v1/geos/resources/nrv/total")
        assert r.status_code == 200
        d = r.json()
        assert d["total_nrv"] > 0

    def test_geos_resources_ec_total(self, client):
        r = client.get("/api/v1/geos/resources/ec/total")
        assert r.status_code == 200
        d = r.json()
        assert d["total_ec"] > 0

    def test_geos_taxes(self, client):
        r = client.get("/api/v1/geos/taxes")
        assert r.status_code == 200
        assert len(r.json()) == 4

    def test_geos_taxes_revenue_total(self, client):
        r = client.get("/api/v1/geos/taxes/revenue/total")
        assert r.status_code == 200
        d = r.json()
        assert d["total_revenue"] > 0
        assert d["total_evasion"] > 0

    def test_geos_projects(self, client):
        r = client.get("/api/v1/geos/projects")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_geos_projects_snn_total(self, client):
        r = client.get("/api/v1/geos/projects/snn/total")
        assert r.status_code == 200
        d = r.json()
        assert d["total_snn"] > 0

    def test_geos_public_services(self, client):
        r = client.get("/api/v1/geos/public-services")
        assert r.status_code == 200
        assert len(r.json()) == 3

    def test_geos_public_services_cs_total(self, client):
        r = client.get("/api/v1/geos/public-services/cs/total")
        assert r.status_code == 200
        d = r.json()
        assert d["total_cs"] > 0
