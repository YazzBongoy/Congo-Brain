"""Tests for MOEG SNN — Surplus National Net economic engine.

SNN = CS + PS + GR + NRV - DWL - EC
"""

import pytest
from congo_brain.services.economic.welfare_model import WelfareModel, EconomyConstraints
from congo_brain.services.economic.resource_optimizer import ResourceOptimizer, ResourceValueChain
from congo_brain.services.economic.investment_allocator import InvestmentAllocator, MOEGProject
from congo_brain.services.economic.nwi import NationalWelfareIndex, NWIComponents
from congo_brain.services.economic.corruption_calculator import CorruptionCalculator, DWLComponents, EnvironmentalCost


class TestWelfareModel:
    def test_empty_welfare(self):
        wm = WelfareModel()
        assert wm.total_snn == 0.0

    def test_single_sector_snn(self):
        wm = WelfareModel()
        wm.add_sector("Énergie", cs=5.0, ps=4.0, revenue=2.0, nrv=3.0, dwl=1.0, ec=0.5)
        # SNN = 5+4+2+3 - 1 - 0.5 = 12.5
        assert wm.total_snn == 12.5

    def test_multi_sector_snn(self):
        wm = WelfareModel()
        wm.add_sector("A", cs=3.0, ps=2.0, revenue=1.0, nrv=1.5, dwl=0.5, ec=0.2)
        wm.add_sector("B", cs=4.0, ps=3.0, revenue=2.0, nrv=2.0, dwl=1.0, ec=0.3)
        # A: 3+2+1+1.5 - 0.5 - 0.2 = 6.8
        # B: 4+3+2+2 - 1 - 0.3 = 9.7
        assert wm.total_snn == 16.5

    def test_nrv_contribution(self):
        wm = WelfareModel()
        wm.add_sector("Mine", cs=1.0, ps=1.0, revenue=1.0, nrv=10.0, dwl=0.5, ec=0.5)
        assert wm.total_nrv == 10.0
        assert wm.total_snn == 12.0  # 1+1+1+10 - 0.5 - 0.5

    def test_environmental_cost_penalty(self):
        wm = WelfareModel()
        wm.add_sector("A", cs=5.0, ps=5.0, revenue=5.0, nrv=5.0, dwl=0.0, ec=3.0)
        wm.add_sector("B", cs=5.0, ps=5.0, revenue=5.0, nrv=5.0, dwl=0.0, ec=0.5)
        # A: 20 - 3 = 17, B: 20 - 0.5 = 19.5
        assert wm.sectors["B"].snn > wm.sectors["A"].snn

    def test_corruption_rate(self):
        wm = WelfareModel()
        wm.add_sector("Test", cs=5.0, ps=5.0, revenue=5.0, nrv=5.0, dwl=4.0, ec=0.0)
        # positive = 20, dwl = 4 => 20%
        assert wm.national_corruption_rate == 20.0

    def test_environmental_rate(self):
        wm = WelfareModel()
        wm.add_sector("Test", cs=5.0, ps=5.0, revenue=5.0, nrv=5.0, dwl=0.0, ec=2.0)
        assert wm.national_environmental_rate == 10.0

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

    def test_sector_breakdown_sorted_by_snn(self):
        wm = WelfareModel()
        wm.add_sector("Low", cs=1.0, ps=1.0, revenue=1.0, nrv=0.5, dwl=0.1, ec=0.1)
        wm.add_sector("High", cs=5.0, ps=5.0, revenue=5.0, nrv=5.0, dwl=0.1, ec=0.1)
        breakdown = wm.get_sector_breakdown()
        assert breakdown[0]["sector"] == "High"

    def test_dashboard_snn_formula(self):
        wm = WelfareModel()
        wm.add_sector("Test", cs=3.0, ps=2.0, revenue=1.0, nrv=1.0, dwl=0.5, ec=0.2)
        d = wm.get_dashboard()
        assert d["model"] == "MOEG"
        assert "SNN" in d["formula"]
        assert "natural_resource_value" in d["components"]
        assert "environmental_cost" in d["components"]


class TestResourceOptimizer:
    def test_load_baseline(self):
        ro = ResourceOptimizer()
        ro.load_baseline()
        assert len(ro.resources) == 7

    def test_total_nrv(self):
        ro = ResourceOptimizer()
        ro.load_baseline()
        assert ro.total_nrv > 0
        assert ro.total_nrv == ro.total_value_added

    def test_capture_rate(self):
        ro = ResourceOptimizer()
        ro.load_baseline()
        assert 0 < ro.overall_capture_rate < 100

    def test_recommendations_with_high_target(self):
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
        assert ro.resources["Diamant"].capture_rate > 50

    def test_dashboard_has_nrv(self):
        ro = ResourceOptimizer()
        ro.load_baseline()
        d = ro.get_dashboard()
        assert "total_value_added" in d
        assert d["total_value_added"] == ro.total_nrv


class TestInvestmentAllocator:
    def test_empty_projects(self):
        ia = InvestmentAllocator()
        ia.set_budget(10000)
        result = ia.optimize()
        assert result["total_cost"] == 0

    def test_single_project_fit(self):
        ia = InvestmentAllocator()
        ia.add_project(MOEGProject(
            name="P1", cost=100, revenue_impact=0.8, jobs_score=0.9,
            local_value_added=0.7,
        ))
        ia.set_budget(200)
        result = ia.optimize()
        assert "P1" in result["allocation"]

    def test_budget_constraint(self):
        ia = InvestmentAllocator()
        ia.add_project(MOEGProject(
            name="P1", cost=500, revenue_impact=0.9, jobs_score=0.8,
            local_value_added=0.9, corruption_risk=0.2, env_impact=0.1, duration_months=12,
        ))
        ia.add_project(MOEGProject(
            name="P2", cost=600, revenue_impact=0.8, jobs_score=0.7,
            local_value_added=0.8, corruption_risk=0.3, env_impact=0.2, duration_months=18,
        ))
        ia.set_budget(800)
        result = ia.optimize()
        assert result["total_cost"] <= 800

    def test_nsb_scoring_maximize_revenue(self):
        p1 = MOEGProject(name="High", cost=100, revenue_impact=0.9, jobs_score=0.5, local_value_added=0.5)
        p2 = MOEGProject(name="Low", cost=100, revenue_impact=0.2, jobs_score=0.5, local_value_added=0.5)
        assert p1.nsb_score() > p2.nsb_score()

    def test_nsb_scoring_maximize_jobs(self):
        p1 = MOEGProject(name="Many", cost=100, jobs_score=0.9, revenue_impact=0.5, local_value_added=0.5)
        p2 = MOEGProject(name="Few", cost=100, jobs_score=0.2, revenue_impact=0.5, local_value_added=0.5)
        assert p1.nsb_score() > p2.nsb_score()

    def test_nsb_scoring_maximize_nrv(self):
        p1 = MOEGProject(name="HighNRV", cost=100, local_value_added=0.9, revenue_impact=0.5, jobs_score=0.5)
        p2 = MOEGProject(name="LowNRV", cost=100, local_value_added=0.1, revenue_impact=0.5, jobs_score=0.5)
        assert p1.nsb_score() > p2.nsb_score()

    def test_nsb_scoring_minimize_corruption(self):
        p1 = MOEGProject(name="Clean", cost=100, corruption_risk=0.1, revenue_impact=0.5, jobs_score=0.5, local_value_added=0.5)
        p2 = MOEGProject(name="Dirty", cost=100, corruption_risk=0.9, revenue_impact=0.5, jobs_score=0.5, local_value_added=0.5)
        assert p1.nsb_score() > p2.nsb_score()

    def test_nsb_scoring_minimize_env_impact(self):
        p1 = MOEGProject(name="Green", cost=100, env_impact=0.1, revenue_impact=0.5, jobs_score=0.5, local_value_added=0.5)
        p2 = MOEGProject(name="Polluted", cost=100, env_impact=0.9, revenue_impact=0.5, jobs_score=0.5, local_value_added=0.5)
        assert p1.nsb_score() > p2.nsb_score()

    def test_nsb_scoring_minimize_duration(self):
        p1 = MOEGProject(name="Fast", cost=100, duration_months=6, revenue_impact=0.5, jobs_score=0.5, local_value_added=0.5)
        p2 = MOEGProject(name="Slow", cost=100, duration_months=120, revenue_impact=0.5, jobs_score=0.5, local_value_added=0.5)
        assert p1.nsb_score() > p2.nsb_score()

    def test_load_baseline(self):
        ia = InvestmentAllocator()
        ia.load_baseline()
        assert len(ia.projects) == 10

    def test_compare_scenarios(self):
        ia = InvestmentAllocator()
        ia.load_baseline()
        scenarios = ia.compare_scenarios([5000, 10000, 20000])
        assert len(scenarios) == 3
        assert scenarios[2]["total_score"] >= scenarios[0]["total_score"]

    def test_dashboard_has_nsb(self):
        ia = InvestmentAllocator()
        ia.load_baseline()
        d = ia.get_dashboard()
        assert "NSB" in d["formula"]
        assert "projects" in d


class TestNationalWelfareIndex:
    def test_perfect_score(self):
        nwi = NationalWelfareIndex()
        comp = NWIComponents(10, 10, 10, 10, 10, 0, 0, 10, 10, 10, 10, 10)
        result = nwi.compute_nwi(comp)
        # Positive weights sum to 0.90, penalties 0 => max is 90
        assert result["nwi_score"] == 90.0
        assert result["rating"] == "Excellent"

    def test_zero_score(self):
        nwi = NationalWelfareIndex()
        comp = NWIComponents(0, 0, 0, 0, 0, 100, 100, 10, 10, 10, 10, 10)
        result = nwi.compute_nwi(comp)
        assert result["nwi_score"] == 0.0

    def test_nrv_in_nwi(self):
        nwi = NationalWelfareIndex()
        high_nrv = NWIComponents(5, 5, 5, 10, 5, 0, 0, 10, 10, 10, 10, 10)
        low_nrv = NWIComponents(5, 5, 5, 1, 5, 0, 0, 10, 10, 10, 10, 10)
        assert nwi.compute_nwi(high_nrv)["nwi_score"] > nwi.compute_nwi(low_nrv)["nwi_score"]

    def test_dwl_penalty(self):
        nwi = NationalWelfareIndex()
        clean = NWIComponents(5, 5, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10)
        dirty = NWIComponents(5, 5, 5, 5, 5, 50, 50, 10, 10, 10, 10, 10)
        assert nwi.compute_nwi(clean)["nwi_score"] > nwi.compute_nwi(dirty)["nwi_score"]

    def test_ec_penalty(self):
        nwi = NationalWelfareIndex()
        green = NWIComponents(5, 5, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10)
        polluted = NWIComponents(5, 5, 5, 5, 5, 5, 50, 10, 10, 10, 10, 10)
        assert nwi.compute_nwi(green)["nwi_score"] > nwi.compute_nwi(polluted)["nwi_score"]

    def test_sector_aggregation(self):
        nwi = NationalWelfareIndex()
        nwi.add_sector("A", NWIComponents(8, 8, 8, 8, 8, 10, 10, 10, 10, 10, 10, 10))
        nwi.add_sector("B", NWIComponents(4, 4, 4, 4, 4, 10, 10, 10, 10, 10, 10, 10))
        result = nwi.compute_nwi()
        # Both have same penalty, averages should give NWI between 0-100
        assert 0 <= result["nwi_score"] <= 100

    def test_rating_thresholds(self):
        nwi = NationalWelfareIndex()
        assert nwi._rate(85) == "Excellent"
        assert nwi._rate(70) == "Bon"
        assert nwi._rate(50) == "Moyen"
        assert nwi._rate(30) == "Faible"
        assert nwi._rate(10) == "Critique"

    def test_dashboard_formula(self):
        nwi = NationalWelfareIndex()
        nwi.add_sector("Test", NWIComponents(5, 5, 5, 5, 5))
        d = nwi.get_dashboard()
        assert "NRV" in d["formula"]
        assert "DWL" in d["formula"]
        assert "EC" in d["formula"]


class TestCorruptionCalculator:
    def test_baseline_costs(self):
        cc = CorruptionCalculator()
        assert cc.dwl.total_dwl == 7.6
        assert cc.ec.total_ec == 4.4
        assert cc.total_costs == 12.0

    def test_costs_pct_gdp(self):
        cc = CorruptionCalculator()
        assert cc.costs_pct_gdp > 0

    def test_component_breakdown_includes_ec(self):
        cc = CorruptionCalculator()
        breakdown = cc.get_component_breakdown()
        categories = {b["category"] for b in breakdown}
        assert "DWL" in categories
        assert "EC" in categories

    def test_scenario_analysis_both(self):
        cc = CorruptionCalculator()
        result = cc.scenario_analysis(dwl_reduction_pct=25, ec_reduction_pct=25)
        assert result["reduction_amount"] > 0
        assert result["snn_improvement"] > 0

    def test_environmental_targets(self):
        cc = CorruptionCalculator()
        targets = cc.environmental_targets()
        assert len(targets) > 0
        assert targets[0]["potential_recovery"] > 0

    def test_anti_corruption_targets(self):
        cc = CorruptionCalculator()
        targets = cc.anti_corruption_targets()
        assert len(targets) > 0

    def test_custom_ec(self):
        cc = CorruptionCalculator()
        cc.set_ec(EnvironmentalCost(deforestation=2.0, pollution=1.0))
        assert cc.ec.total_ec == 3.0
        assert cc.total_costs == cc.dwl.total_dwl + 3.0

    def test_dashboard_has_snn(self):
        cc = CorruptionCalculator()
        d = cc.get_dashboard()
        assert "SNN_costs" in d["formula"]
        assert "ec" in d
        assert "environmental_targets" in d
