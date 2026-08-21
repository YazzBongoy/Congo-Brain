"""Tests for GEOS Predictive Model."""

import pytest

from congo_brain.services.ia_gov.predictor import (
    SCENARIOS,
    PredictiveModel,
    Scenario,
    YearProjection,
)
from congo_brain.services.ia_gov.snn_engine import SNNOptimizationEngine


class TestScenario:
    def test_scenario_to_dict(self):
        s = Scenario(name="Test", description="Desc", cs_growth=0.05)
        d = s.to_dict()
        assert d["name"] == "Test"
        assert d["cs_growth"] == 0.05

    def test_preset_scenarios_exist(self):
        assert "baseline" in SCENARIOS
        assert "investissement_minier" in SCENARIOS
        assert "reforme_fiscale" in SCENARIOS
        assert "anti_corruption" in SCENARIOS
        assert "transition_verte" in SCENARIOS
        assert "optimiste" in SCENARIOS
        assert "pessimiste" in SCENARIOS

    def test_preset_scenarios_have_names(self):
        for key, s in SCENARIOS.items():
            assert s.name
            assert s.description


class TestYearProjection:
    def test_to_dict(self):
        p = YearProjection(year=1, cs=100, ps=50, gr=30, nrv=20, dwl=10, ec=5, snn=185)
        d = p.to_dict()
        assert d["year"] == 1
        assert d["snn"] == 185
        assert d["cs"] == 100


class TestPredictiveModel:
    def test_init(self):
        m = PredictiveModel()
        assert m.base_snn == 0

    def test_set_baseline(self):
        m = PredictiveModel()
        m.set_baseline(cs=100, ps=50, gr=30, nrv=20, dwl=10, ec=5)
        assert m.base_snn == 185  # 100+50+30+20-10-5

    def test_load_from_snn_engine(self):
        engine = SNNOptimizationEngine()
        engine.load_drc_baseline()
        m = PredictiveModel()
        m.load_from_snn_engine(engine)
        assert m.base_snn > 0

    def test_baseline_zero(self):
        m = PredictiveModel()
        assert m.base_snn == 0

    def test_project_baseline(self):
        m = PredictiveModel()
        m.set_baseline(cs=100, ps=50, gr=30, nrv=20, dwl=10, ec=5)
        r = m.project(SCENARIOS["baseline"], years=5, monte_carlo_runs=10)
        assert r.horizon_years == 5
        assert len(r.projections) == 5
        assert r.base_snn == 185
        assert r.final_snn != 0

    def test_project_optimiste_grows(self):
        m = PredictiveModel()
        m.set_baseline(cs=100, ps=50, gr=30, nrv=20, dwl=10, ec=5)
        r = m.project(SCENARIOS["optimiste"], years=5, monte_carlo_runs=10)
        assert r.final_snn > r.base_snn

    def test_project_pessimiste_declines(self):
        m = PredictiveModel()
        m.set_baseline(cs=100, ps=50, gr=30, nrv=20, dwl=10, ec=5)
        r = m.project(SCENARIOS["pessimiste"], years=5, monte_carlo_runs=10)
        # Pessimistic should have negative change_pct
        assert r.snn_change_pct < 0

    def test_prediction_result_to_dict(self):
        m = PredictiveModel()
        m.set_baseline(cs=100, ps=50, gr=30, nrv=20, dwl=10, ec=5)
        r = m.project(SCENARIOS["baseline"], years=3, monte_carlo_runs=10)
        d = r.to_dict()
        assert "scenario" in d
        assert "projections" in d
        assert "ci_5" in d
        assert "ci_95" in d
        assert len(d["projections"]) == 3

    def test_compare_scenarios(self):
        m = PredictiveModel()
        m.set_baseline(cs=100, ps=50, gr=30, nrv=20, dwl=10, ec=5)
        c = m.compare_scenarios(years=5)
        assert "scenarios" in c
        assert "ranking" in c
        assert len(c["ranking"]) == 7

    def test_compare_scenarios_ranking_order(self):
        m = PredictiveModel()
        m.set_baseline(cs=100, ps=50, gr=30, nrv=20, dwl=10, ec=5)
        c = m.compare_scenarios(years=5)
        rankings = c["ranking"]
        for i in range(len(rankings) - 1):
            assert rankings[i]["final_snn"] >= rankings[i + 1]["final_snn"]

    def test_get_dashboard(self):
        m = PredictiveModel()
        m.set_baseline(cs=100, ps=50, gr=30, nrv=20, dwl=10, ec=5)
        d = m.get_dashboard(years=5)
        assert d["model"] == "GEOS Predictive"
        assert d["horizon_years"] == 5
        assert "comparison" in d

    def test_monte_carlo_confidence_interval(self):
        m = PredictiveModel()
        m.set_baseline(cs=100, ps=50, gr=30, nrv=20, dwl=10, ec=5)
        r = m.project(SCENARIOS["baseline"], years=5, monte_carlo_runs=100)
        assert r.ci_5 <= r.mean_final_snn <= r.ci_95

    def test_investment_scenario_higher_snn(self):
        m = PredictiveModel()
        m.set_baseline(cs=100, ps=50, gr=30, nrv=20, dwl=10, ec=5)
        r_base = m.project(SCENARIOS["baseline"], years=5, monte_carlo_runs=10)
        r_invest = m.project(SCENARIOS["investissement_minier"], years=5, monte_carlo_runs=10)
        assert r_invest.final_snn > r_base.final_snn


class TestGEOSPredictiveAPI:
    @pytest.fixture(autouse=True)
    def _authenticate(self, client, auth_headers):
        client.headers.update(auth_headers)

    def test_list_scenarios(self, client):
        r = client.get("/api/v1/geos/predictions/scenarios")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 5
        assert any(s["name"] == "Baseline (statu quo)" for s in data)

    def test_compare_scenarios(self, client):
        r = client.get("/api/v1/geos/predictions/compare?years=5")
        assert r.status_code == 200
        d = r.json()
        assert "ranking" in d
        assert len(d["ranking"]) >= 5

    def test_predict_baseline(self, client):
        r = client.get("/api/v1/geos/predictions/baseline?years=5")
        assert r.status_code == 200
        d = r.json()
        assert d["scenario"] == "Baseline (statu quo)"
        assert len(d["projections"]) == 5
        assert d["final_snn"] != 0

    def test_predict_unknown(self, client):
        r = client.get("/api/v1/geos/predictions/inconnu")
        assert r.status_code == 404

    def test_predict_optimiste(self, client):
        r = client.get("/api/v1/geos/predictions/optimiste?years=10")
        assert r.status_code == 200
        d = r.json()
        assert len(d["projections"]) == 10

    def test_predict_investissement(self, client):
        r = client.get("/api/v1/geos/predictions/investissement_minier")
        assert r.status_code == 200
        d = r.json()
        assert d["scenario"] == "Investissement minier massif"
