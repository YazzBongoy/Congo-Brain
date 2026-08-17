"""Tests for IA GOV — Intelligence Artificielle pour la Gouvernance.

Pipeline: Collecte → Intelligence → Optimisation → Dashboard → Décision
"""

import pytest
from congo_brain.services.ia_gov.collectors import DataCollector, BudgetData, EconomicData, SocialData
from congo_brain.services.ia_gov.intelligence import IntelligenceEngine, SurplusEstimate, AnalysisResult
from congo_brain.services.ia_gov.optimizer import GovOptimizer, GovDecision
from congo_brain.services.ia_gov.dashboard import GovDashboard


class TestDataCollector:
    def test_load_baseline(self):
        dc = DataCollector()
        dc.load_drc_baseline()
        assert dc.budget is not None
        assert dc.economy is not None
        assert dc.social is not None

    def test_budget_balance(self):
        dc = DataCollector()
        dc.load_drc_baseline()
        b = dc.get_budget_data()
        assert b.budget_balance < 0  # deficit

    def test_gdp_data(self):
        dc = DataCollector()
        dc.load_drc_baseline()
        e = dc.get_economic_data()
        assert e.gdp == 55_000
        assert e.gdp_growth > 0

    def test_social_data(self):
        dc = DataCollector()
        dc.load_drc_baseline()
        s = dc.get_social_data()
        assert s.population > 100
        assert s.poverty_rate > 50

    def test_get_all(self):
        dc = DataCollector()
        dc.load_drc_baseline()
        all_data = dc.get_all()
        assert "budget" in all_data
        assert "economy" in all_data
        assert "social" in all_data

    def test_historical(self):
        dc = DataCollector()
        history = dc.get_historical(5)
        assert len(history) == 5
        assert history[0]["year"] < history[-1]["year"]

    def test_province_data(self):
        dc = DataCollector()
        dc.load_drc_baseline()
        assert "Kinshasa" in dc.province_data
        assert dc.province_data["Kinshasa"]["gdp_share"] > 0


class TestIntelligenceEngine:
    def _get_data(self):
        dc = DataCollector()
        dc.load_drc_baseline()
        return dc.get_all()

    def test_analysis_produces_results(self):
        data = self._get_data()
        engine = IntelligenceEngine()
        result = engine.analyze(data["budget"], data["economy"], data["social"])
        assert isinstance(result, AnalysisResult)
        assert result.national_snn != 0

    def test_sector_surpluses(self):
        data = self._get_data()
        engine = IntelligenceEngine()
        result = engine.analyze(data["budget"], data["economy"], data["social"])
        assert len(result.sector_surpluses) > 0

    def test_snn_components(self):
        data = self._get_data()
        engine = IntelligenceEngine()
        result = engine.analyze(data["budget"], data["economy"], data["social"])
        for s in result.sector_surpluses:
            assert s.consumer_surplus >= 0
            assert s.producer_surplus >= 0
            assert s.deadweight_loss >= 0

    def test_alerts_detected(self):
        data = self._get_data()
        engine = IntelligenceEngine()
        result = engine.analyze(data["budget"], data["economy"], data["social"])
        assert len(result.alerts) > 0  # DRC has many governance issues

    def test_trends_analyzed(self):
        data = self._get_data()
        engine = IntelligenceEngine()
        result = engine.analyze(data["budget"], data["economy"], data["social"])
        assert len(result.trends) > 0

    def test_recommendations_generated(self):
        data = self._get_data()
        engine = IntelligenceEngine()
        result = engine.analyze(data["budget"], data["economy"], data["social"])
        assert len(result.recommendations) > 0

    def test_decision_matrix(self):
        data = self._get_data()
        engine = IntelligenceEngine()
        result = engine.analyze(data["budget"], data["economy"], data["social"])
        assert len(result.decision_matrix) > 0
        # Should be sorted by net benefit
        for i in range(len(result.decision_matrix) - 1):
            assert result.decision_matrix[i]["net_benefit"] >= result.decision_matrix[i+1]["net_benefit"]


class TestGovOptimizer:
    def test_load_baseline(self):
        opt = GovOptimizer()
        opt.load_baseline_decisions()
        assert len(opt.decisions) > 0

    def test_decision_snn(self):
        d = GovDecision("Test", "Énergie", 100, expected_cs=5.0, expected_ps=5.0,
                         expected_gr=2.0, expected_nrv=0.0, expected_dwl=0.5, expected_ec=0.3)
        assert d.expected_snn == 11.2  # 5+5+2+0 - 0.5 - 0.3

    def test_optimize_with_budget(self):
        opt = GovOptimizer()
        opt.load_baseline_decisions()
        opt.set_budget(5000)
        result = opt.optimize()
        assert result.total_cost <= 5000
        assert result.total_snn > 0
        assert len(result.decisions) > 0

    def test_optimize_full_budget(self):
        opt = GovOptimizer()
        opt.load_baseline_decisions()
        opt.set_budget(100_000)  # very large budget
        result = opt.optimize()
        # Should fund all decisions
        assert len(result.decisions) == len(opt.decisions)

    def test_compare_scenarios(self):
        opt = GovOptimizer()
        opt.load_baseline_decisions()
        opt.set_budget(10_000)
        scenarios = opt.compare_scenarios([5000, 10000, 20000])
        assert len(scenarios) == 3
        # Higher budget should yield higher SNN
        assert scenarios[2]["total_snn"] >= scenarios[0]["total_snn"]

    def test_sensitivity_analysis(self):
        opt = GovOptimizer()
        opt.load_baseline_decisions()
        opt.set_budget(10_000)
        sensitivity = opt.get_sensitivity_analysis()
        assert len(sensitivity) == 5


class TestGovDashboard:
    def test_full_analysis(self):
        dash = GovDashboard()
        result = dash.run_full_analysis(10_000)
        assert "pipeline" in result
        assert "data" in result
        assert "analysis" in result
        assert "optimization" in result
        assert "summary" in result

    def test_welfare_status(self):
        dash = GovDashboard()
        status = dash.get_welfare_status()
        assert "national_snn" in status
        assert "alerts_count" in status

    def test_sector_analysis(self):
        dash = GovDashboard()
        sectors = dash.get_sector_analysis()
        assert len(sectors) > 0
        assert "snn" in sectors[0]

    def test_decision_support(self):
        dash = GovDashboard()
        support = dash.get_decision_support(10_000)
        assert "optimal_allocation" in support
        assert "scenarios" in support
        assert "sensitivity" in support

    def test_alerts(self):
        dash = GovDashboard()
        alerts = dash.get_alerts()
        assert isinstance(alerts, list)

    def test_recommendations(self):
        dash = GovDashboard()
        recs = dash.get_recommendations()
        assert isinstance(recs, list)

    def test_historical(self):
        dash = GovDashboard()
        data = dash.get_historical(3)
        assert len(data) == 3
