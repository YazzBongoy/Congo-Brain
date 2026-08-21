"""Tests for IA GOV — 8 modules architecture.

1. Resource Optimization Engine
2. Consumer Surplus Engine
3. Producer Surplus Engine
4. National Resource Engine
5. Governance Score
6. Corruption Detector
7. National Digital Twin
8. Decision AI
"""

from congo_brain.services.ia_gov.collectors import DataCollector
from congo_brain.services.ia_gov.consumer_surplus import ConsumerSurplusEngine, PublicService
from congo_brain.services.ia_gov.corruption_detector import CorruptionDetectionEngine
from congo_brain.services.ia_gov.decision_ai import DecisionAI
from congo_brain.services.ia_gov.digital_twin import NationalDigitalTwin, ProvinceTwin
from congo_brain.services.ia_gov.governance_score import GovernanceScoreEngine, MinistryScore
from congo_brain.services.ia_gov.national_resource import Mine, NationalResourceEngine
from congo_brain.services.ia_gov.producer_surplus import Enterprise, ProducerSurplusEngine
from congo_brain.services.ia_gov.resource_optimizer import ResourceOptimizationEngine

# ── Module 1: Resource Optimization Engine ─────────────────────


class TestResourceOptimizationEngine:
    def test_load_baseline(self):
        e = ResourceOptimizationEngine()
        e.load_drc_baseline()
        assert len(e.sectors) > 0
        assert len(e.constraints) > 0

    def test_total_welfare(self):
        e = ResourceOptimizationEngine()
        e.load_drc_baseline()
        assert e.total_welfare != 0

    def test_optimize(self):
        e = ResourceOptimizationEngine()
        e.load_drc_baseline()
        result = e.optimize()
        assert "total_welfare" in result
        assert "allocation" in result

    def test_simulate_policy(self):
        e = ResourceOptimizationEngine()
        e.load_drc_baseline()
        result = e.simulate_policy("Test", {"Énergie": {"cs_delta": 2.0}})
        assert "welfare_delta" in result
        assert result["impact"] == "positif"

    def test_constraints(self):
        e = ResourceOptimizationEngine()
        e.load_drc_baseline()
        assert "Budget" in e.constraints
        assert "Inflation" in e.constraints

    def test_dashboard(self):
        e = ResourceOptimizationEngine()
        e.load_drc_baseline()
        d = e.get_dashboard()
        assert d["model"] == "ResourceOptimizationEngine"
        assert "formula" in d


# ── Module 2: Consumer Surplus Engine ──────────────────────────


class TestConsumerSurplusEngine:
    def test_load_baseline(self):
        e = ConsumerSurplusEngine()
        e.load_baseline()
        assert len(e.services) > 0

    def test_cs_calculation(self):
        s = PublicService(
            "Test", willingness_to_pay=20, actual_price=10, quality_score=7, access_time_hours=2, indirect_cost=3
        )
        assert s.consumer_surplus == 7  # 20 - 10 - 3
        assert s.effective_cs > 0

    def test_total_cs(self):
        e = ConsumerSurplusEngine()
        e.load_baseline()
        assert e.total_cs > 0

    def test_cs_ranking(self):
        e = ConsumerSurplusEngine()
        e.load_baseline()
        ranking = e.get_cs_ranking()
        assert len(ranking) > 0
        assert ranking[0]["effective_cs"] >= ranking[-1]["effective_cs"]

    def test_simulate_improvement(self):
        e = ConsumerSurplusEngine()
        e.load_baseline()
        result = e.simulate_improvement("Eau potable", quality_delta=2.0, price_delta=-2.0)
        assert "cs_delta" in result
        assert result["cs_delta"] >= 0  # non-negative improvement

    def test_dashboard(self):
        e = ConsumerSurplusEngine()
        e.load_baseline()
        d = e.get_dashboard()
        assert "formula" in d
        assert "services" in d


# ── Module 3: Producer Surplus Engine ──────────────────────────


class TestProducerSurplusEngine:
    def test_load_baseline(self):
        e = ProducerSurplusEngine()
        e.load_baseline()
        assert len(e.enterprises) > 0

    def test_ps_calculation(self):
        ent = Enterprise(
            "Test",
            "Industrie",
            revenue=100,
            production_cost=40,
            tax_burden=20,
            admin_cost=5,
            corruption_cost=5,
            logistics_cost=10,
            energy_cost=10,
            employees=50,
        )
        assert ent.producer_surplus == 10  # 100 - 90
        assert ent.ps_margin == 10.0

    def test_total_ps(self):
        e = ProducerSurplusEngine()
        e.load_baseline()
        assert e.total_ps > 0

    def test_simulate_reform(self):
        e = ProducerSurplusEngine()
        e.load_baseline()
        result = e.simulate_reform("Test", tax_reduction=0.2)
        assert "ps_delta" in result
        assert result["ps_delta"] > 0

    def test_corruption_drag(self):
        e = ProducerSurplusEngine()
        e.load_baseline()
        assert e.total_corruption_drag > 0

    def test_dashboard(self):
        e = ProducerSurplusEngine()
        e.load_baseline()
        d = e.get_dashboard()
        assert "total_ps" in d
        assert "enterprises" in d


# ── Module 4: National Resource Engine ─────────────────────────


class TestNationalResourceEngine:
    def test_load_baseline(self):
        e = NationalResourceEngine()
        e.load_baseline()
        assert len(e.mines) > 0

    def test_mine_calculations(self):
        m = Mine(
            "Test",
            "Haut-Katanga",
            "Cuivre",
            annual_production_tons=100_000,
            market_value_per_ton=8000,
            local_processing_pct=10,
            tax_rate=35,
            employees=500,
        )
        assert m.gross_value == 800  # 100k * 8k / 1M
        assert m.value_added > m.gross_value
        assert m.capture_rate > 0

    def test_total_values(self):
        e = NationalResourceEngine()
        e.load_baseline()
        assert e.total_gross_value > 0
        assert e.total_tax_revenue > 0

    def test_mineral_breakdown(self):
        e = NationalResourceEngine()
        e.load_baseline()
        breakdown = e.get_mineral_breakdown()
        assert "Cuivre" in breakdown
        assert "Cobalt" in breakdown

    def test_compare_scenarios(self):
        e = NationalResourceEngine()
        e.load_baseline()
        scenarios = e.compare_scenarios(
            "Kamoa-Kakula",
            [
                {"name": "Export brut", "local_processing_pct": 0},
                {"name": "Transformation locale", "local_processing_pct": 50},
            ],
        )
        assert len(scenarios) == 2
        assert scenarios[1]["value_added"] > scenarios[0]["value_added"]

    def test_dashboard(self):
        e = NationalResourceEngine()
        e.load_baseline()
        d = e.get_dashboard()
        assert "mines" in d
        assert "mineral_breakdown" in d


# ── Module 5: Governance Score ─────────────────────────────────


class TestGovernanceScoreEngine:
    def test_load_baseline(self):
        e = GovernanceScoreEngine()
        e.load_baseline()
        assert len(e.ministries) > 0

    def test_score_calculation(self):
        m = MinistryScore("Test", optimization=80, transparency=60, performance=70, satisfaction=50)
        # 0.4*80 + 0.2*60 + 0.2*70 + 0.2*50 = 32+12+14+10 = 68
        assert m.governance_score == 68.0
        assert m.rating == "Bon"

    def test_average_score(self):
        e = GovernanceScoreEngine()
        e.load_baseline()
        assert 0 < e.average_score < 100

    def test_ranking(self):
        e = GovernanceScoreEngine()
        e.load_baseline()
        ranking = e.get_ranking()
        assert len(ranking) > 0
        assert ranking[0]["governance_score"] >= ranking[-1]["governance_score"]

    def test_improvement_targets(self):
        e = GovernanceScoreEngine()
        e.load_baseline()
        targets = e.get_improvement_targets()
        assert len(targets) > 0

    def test_dashboard(self):
        e = GovernanceScoreEngine()
        e.load_baseline()
        d = e.get_dashboard()
        assert "national_score" in d
        assert "formula" in d


# ── Module 6: Corruption Detector ─────────────────────────────


class TestCorruptionDetectionEngine:
    def test_load_baseline(self):
        e = CorruptionDetectionEngine()
        e.load_baseline()
        assert len(e.anomalies) > 0

    def test_risk_levels(self):
        e = CorruptionDetectionEngine()
        e.load_baseline()
        assert e.critical_count > 0 or e.high_count > 0

    def test_total_at_risk(self):
        e = CorruptionDetectionEngine()
        e.load_baseline()
        assert e.total_amount_at_risk > 0

    def test_by_sector(self):
        e = CorruptionDetectionEngine()
        e.load_baseline()
        by_sector = e.get_by_sector()
        assert "Infrastructure" in by_sector

    def test_risk_summary(self):
        e = CorruptionDetectionEngine()
        e.load_baseline()
        summary = e.get_risk_summary()
        assert "total_anomalies" in summary
        assert "average_risk_score" in summary

    def test_dashboard(self):
        e = CorruptionDetectionEngine()
        e.load_baseline()
        d = e.get_dashboard()
        assert "risk_summary" in d
        assert "anomalies" in d


# ── Module 7: National Digital Twin ───────────────────────────


class TestNationalDigitalTwin:
    def test_load_baseline(self):
        t = NationalDigitalTwin()
        t.load_baseline()
        assert len(t.provinces) > 0

    def test_province_calculations(self):
        p = ProvinceTwin(
            "Test",
            population=5.0,
            gdp=2000,
            budget=300,
            electricity_access=30,
            water_access=40,
            internet_access=15,
            health_facilities=50,
            schools=300,
            poverty_rate=60,
            literacy_rate=70,
            security_index=50,
            governance_score=40,
        )
        assert p.gdp_per_capita == 400
        assert p.infrastructure_index > 0
        assert p.development_index > 0

    def test_total_population(self):
        t = NationalDigitalTwin()
        t.load_baseline()
        assert t.total_population > 40  # 8 major provinces ~54.5M

    def test_simulate_investment(self):
        t = NationalDigitalTwin()
        t.load_baseline()
        result = t.simulate_investment("Kinshasa", "énergie", 500)
        assert "expected_gdp_impact" in result
        assert "poverty_reduction_pct" in result

    def test_compare_provinces(self):
        t = NationalDigitalTwin()
        t.load_baseline()
        ranked = t.compare_provinces(3)
        assert len(ranked) == 3

    def test_dashboard(self):
        t = NationalDigitalTwin()
        t.load_baseline()
        d = t.get_dashboard()
        assert "provinces" in d
        assert "total_gdp" in d


# ── Module 8: Decision AI ─────────────────────────────────────


class TestDecisionAI:
    def test_answer_investir(self):
        ai = DecisionAI()
        result = ai.answer("Où investir 500 millions de dollars?", 500)
        assert len(result.allocations) > 0
        assert result.justification != ""

    def test_answer_pauvreté(self):
        ai = DecisionAI()
        result = ai.answer("Comment réduire la pauvreté?", 1000)
        assert any(a["pct"] > 20 for a in result.allocations)

    def test_answer_corruption(self):
        ai = DecisionAI()
        result = ai.answer("Comment réduire la corruption?", 300)
        assert len(result.allocations) > 0

    def test_answer_tva(self):
        ai = DecisionAI()
        result = ai.answer("Quel impact d'une baisse de la TVA?", 200)
        assert len(result.allocations) > 0

    def test_budget_scaling(self):
        ai = DecisionAI()
        r1 = ai.answer("Où investir?", 100)
        r2 = ai.answer("Où investir?", 1000)
        assert r2.snn_impact > r1.snn_impact

    def test_default_answer(self):
        ai = DecisionAI()
        result = ai.answer("question complètement inconnue", 500)
        assert len(result.allocations) > 0
        assert result.confidence == 50

    def test_dashboard(self):
        ai = DecisionAI()
        d = ai.get_dashboard()
        assert "available_topics" in d
        assert len(d["available_topics"]) > 0


# ── Collector ──────────────────────────────────────────────────


class TestDataCollector:
    def test_load_baseline(self):
        dc = DataCollector()
        dc.load_drc_baseline()
        assert dc.budget is not None
        assert dc.economy is not None
        assert dc.social is not None

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
