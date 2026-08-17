"""Tests for MOEG Economic Engine — welfare model, resources, allocator, NWI, corruption."""

import pytest
from congo_brain.services.economic.welfare_model import WelfareModel, EconomyConstraints, SectorWelfare
from congo_brain.services.economic.resource_optimizer import ResourceOptimizer, ResourceValueChain
from congo_brain.services.economic.investment_allocator import InvestmentAllocator, MOEGProject
from congo_brain.services.economic.nwi import NationalWelfareIndex, NWIComponents
from congo_brain.services.economic.corruption_calculator import CorruptionCalculator, DWLComponents


class TestWelfareModel:
    def test_empty_welfare(self):
        wm = WelfareModel()
        assert wm.total_welfare == 0.0

    def test_single_sector(self):
        wm = WelfareModel()
        wm.add_sector("Énergie", cs=5.0, ps=4.0, revenue=2.0, dwl=1.0)
        assert wm.total_welfare == 10.0  # 5+4+2-1

    def test_multi_sector(self):
        wm = WelfareModel()
        wm.add_sector("A", cs=3.0, ps=2.0, revenue=1.0, dwl=0.5)
        wm.add_sector("B", cs=4.0, ps=3.0, revenue=2.0, dwl=1.0)
        assert wm.total_welfare == 13.5  # (3+2+1-0.5)=5.5 + (4+3+2-1)=8.0

    def test_corruption_rate(self):
        wm = WelfareModel()
        wm.add_sector("Test", cs=5.0, ps=5.0, revenue=5.0, dwl=3.0)
        assert wm.national_corruption_rate == 20.0  # 3/15*100

    def test_constraints_met(self):
        wm = WelfareModel()
        wm.set_constraints(EconomyConstraints(
            budget_ceiling=10.0, revenue=12.0,
            current_debt_to_gdp=40.0, current_inflation=3.0,
        ))
        assert wm.constraints.all_constraints_met

    def test_constraints_breach(self):
        wm = WelfareModel()
        wm.set_constraints(EconomyConstraints(
            budget_ceiling=15.0, revenue=12.0,
            current_debt_to_gdp=40.0, current_inflation=3.0,
        ))
        assert not wm.constraints.budget_balanced

    def test_sector_breakdown_sorted(self):
        wm = WelfareModel()
        wm.add_sector("Low", cs=1.0, ps=1.0, revenue=1.0, dwl=0.1)
        wm.add_sector("High", cs=5.0, ps=5.0, revenue=5.0, dwl=0.1)
        breakdown = wm.get_sector_breakdown()
        assert breakdown[0]["sector"] == "High"

    def test_dashboard_structure(self):
        wm = WelfareModel()
        wm.add_sector("Test", cs=3.0, ps=2.0, revenue=1.0, dwl=0.5)
        d = wm.get_dashboard()
        assert d["model"] == "MOEG"
        assert "welfare_function" in d
        assert "constraints" in d


class TestResourceOptimizer:
    def test_load_baseline(self):
        ro = ResourceOptimizer()
        ro.load_baseline()
        assert len(ro.resources) == 7

    def test_total_value(self):
        ro = ResourceOptimizer()
        ro.load_baseline()
        assert ro.total_value > 0

    def test_capture_rate(self):
        ro = ResourceOptimizer()
        ro.load_baseline()
        assert 0 < ro.overall_capture_rate < 100

    def test_recommendations(self):
        ro = ResourceOptimizer()
        ro.load_baseline()
        ro.set_target_capture_rate(80.0)
        recs = ro.get_optimization_recommendations()
        assert len(recs) > 0
        assert recs[0]["potential_additional_value"] > 0

    def test_custom_resource(self):
        ro = ResourceOptimizer()
        ro.add_resource(ResourceValueChain(
            resource="Diamant", extraction_value=1.0,
            transformation_value=0.8, export_value=0.5,
        ))
        assert "Diamant" in ro.resources
        assert ro.resources["Diamant"].capture_rate > 50

    def test_dashboard_structure(self):
        ro = ResourceOptimizer()
        ro.load_baseline()
        d = ro.get_dashboard()
        assert d["model"] == "ResourceOptimizer"
        assert "resources" in d
        assert "recommendations" in d


class TestInvestmentAllocator:
    def test_empty_projects(self):
        ia = InvestmentAllocator()
        ia.set_budget(10000)
        result = ia.optimize()
        assert result["total_cost"] == 0

    def test_single_project_fit(self):
        ia = InvestmentAllocator()
        ia.add_project(MOEGProject(name="P1", cost=100, cs_impact=0.8, ps_impact=0.9))
        ia.set_budget(200)
        result = ia.optimize()
        assert "P1" in result["allocation"]
        assert result["allocation"]["P1"] == 1.0

    def test_budget_constraint(self):
        ia = InvestmentAllocator()
        ia.add_project(MOEGProject(name="P1", cost=500, cs_impact=0.9))
        ia.add_project(MOEGProject(name="P2", cost=600, cs_impact=0.8))
        ia.set_budget(800)
        result = ia.optimize()
        assert result["total_cost"] <= 800

    def test_project_ranking(self):
        ia = InvestmentAllocator()
        ia.add_project(MOEGProject(name="Low", cost=100, cs_impact=0.2, ps_impact=0.2))
        ia.add_project(MOEGProject(name="High", cost=100, cs_impact=0.9, ps_impact=0.9))
        rankings = ia.get_project_scores()
        assert rankings[0]["name"] == "High"

    def test_load_baseline(self):
        ia = InvestmentAllocator()
        ia.load_baseline()
        assert len(ia.projects) == 10

    def test_compare_scenarios(self):
        ia = InvestmentAllocator()
        ia.load_baseline()
        scenarios = ia.compare_scenarios([5000, 10000, 20000])
        assert len(scenarios) == 3
        # Higher budget should yield higher score
        assert scenarios[2]["total_score"] >= scenarios[0]["total_score"]

    def test_dashboard_structure(self):
        ia = InvestmentAllocator()
        ia.load_baseline()
        d = ia.get_dashboard()
        assert d["model"] == "InvestmentAllocator"
        assert "projects" in d


class TestNationalWelfareIndex:
    def test_perfect_score(self):
        nwi = NationalWelfareIndex()
        comp = NWIComponents(10, 10, 10, 10, 10, 10, 10, 10)
        result = nwi.compute_nwi(comp)
        assert result["nwi_score"] == 100.0
        assert result["rating"] == "Excellent"

    def test_zero_score(self):
        nwi = NationalWelfareIndex()
        comp = NWIComponents(0, 0, 0, 0, 10, 10, 10, 10)
        result = nwi.compute_nwi(comp)
        assert result["nwi_score"] == 0.0
        assert result["rating"] == "Critique"

    def test_sector_aggregation(self):
        nwi = NationalWelfareIndex()
        nwi.add_sector("A", NWIComponents(8, 8, 8, 8, 10, 10, 10, 10))
        nwi.add_sector("B", NWIComponents(4, 4, 4, 4, 10, 10, 10, 10))
        result = nwi.compute_nwi()
        # Average of 80 and 40 = 60 for each component
        assert result["nwi_score"] == 60.0

    def test_rating_thresholds(self):
        nwi = NationalWelfareIndex()
        assert nwi._rate(85) == "Excellent"
        assert nwi._rate(70) == "Bon"
        assert nwi._rate(50) == "Moyen"
        assert nwi._rate(30) == "Faible"
        assert nwi._rate(10) == "Critique"

    def test_dashboard_structure(self):
        nwi = NationalWelfareIndex()
        nwi.add_sector("Test", NWIComponents(5, 5, 5, 5))
        d = nwi.get_dashboard()
        assert d["model"] == "NationalWelfareIndex"
        assert "overall" in d
        assert "sectors" in d


class TestCorruptionCalculator:
    def test_baseline_dwl(self):
        cc = CorruptionCalculator()
        assert cc.dwl.total_dwl == 7.6  # 2.5+1.2+0.8+0.6+1.0+1.5

    def test_dwl_pct_gdp(self):
        cc = CorruptionCalculator()
        assert cc.dwl_pct_gdp > 0

    def test_component_breakdown(self):
        cc = CorruptionCalculator()
        breakdown = cc.get_component_breakdown()
        assert len(breakdown) == 6
        assert breakdown[0]["component"] == "Corruption"  # largest

    def test_scenario_analysis(self):
        cc = CorruptionCalculator()
        result = cc.scenario_analysis(25)
        assert result["reduction_amount"] > 0
        assert result["recovered_gdp_percentage"] > 0

    def test_anti_corruption_targets(self):
        cc = CorruptionCalculator()
        targets = cc.anti_corruption_targets()
        assert len(targets) > 0
        assert targets[0]["potential_recovery"] > 0

    def test_custom_dwl(self):
        cc = CorruptionCalculator()
        cc.set_dwl(DWLComponents(corruption=1.0, fraud=0.5, tax_evasion=0.5))
        assert cc.dwl.total_dwl == 2.0

    def test_dashboard_structure(self):
        cc = CorruptionCalculator()
        d = cc.get_dashboard()
        assert d["model"] == "CorruptionCalculator"
        assert "dwl" in d
        assert "scenarios" in d
        assert "anti_corruption_targets" in d
