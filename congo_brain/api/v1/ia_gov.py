"""IA GOV API — Intelligence Artificielle pour la Gouvernance (8 modules).

Modules:
    1. Resource Optimization Engine
    2. Consumer Surplus Engine
    3. Producer Surplus Engine
    4. National Resource Engine
    5. Governance Score
    6. Corruption Detector
    7. National Digital Twin
    8. Decision AI

Endpoints:
    /api/v1/ia-gov/dashboard          — Vue complète
    /api/v1/ia-gov/optimizer          — Moteur d'optimisation SNN
    /api/v1/ia-gov/consumer-surplus   — CS par service public
    /api/v1/ia-gov/producer-surplus   — PS par entreprise
    /api/v1/ia-gov/resources          — Mines et ressources
    /api/v1/ia-gov/governance         — Scores ministères
    /api/v1/ia-gov/corruption         — Détection anomalies
    /api/v1/ia-gov/twin               — Jumeau numérique RDC
    /api/v1/ia-gov/decision           — IA décisionnelle
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from congo_brain.core.database import get_db
from congo_brain.core.rbac import Permission
from congo_brain.core.security import require_permission
from congo_brain.services.audit_service import record_audit_event
from congo_brain.services.ia_gov.collectors import DataCollector
from congo_brain.services.ia_gov.consumer_surplus import ConsumerSurplusEngine
from congo_brain.services.ia_gov.corruption_detector import CorruptionDetectionEngine
from congo_brain.services.ia_gov.decision_ai import DecisionAI
from congo_brain.services.ia_gov.digital_twin import NationalDigitalTwin
from congo_brain.services.ia_gov.governance_score import GovernanceScoreEngine
from congo_brain.services.ia_gov.national_resource import NationalResourceEngine
from congo_brain.services.ia_gov.producer_surplus import ProducerSurplusEngine
from congo_brain.services.ia_gov.resource_optimizer import ResourceOptimizationEngine

router = APIRouter(
    prefix="/ia-gov",
    tags=["IA GOV"],
    dependencies=[Depends(require_permission(Permission.NATIONAL_ANALYTICS_READ))],
)


class DecisionRequest(BaseModel):
    question: str
    budget: float = 500.0


class PolicySimulation(BaseModel):
    policy_name: str
    sector_changes: dict[str, dict]


class InvestmentSimulation(BaseModel):
    province: str
    sector: str
    amount: float


# ── Full Dashboard ─────────────────────────────────────────────


@router.get("/dashboard")
def ia_gov_full_dashboard(
    budget: float = Query(10_000, description="Budget M USD"),
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    """Vue complète des 8 modules IA GOV."""
    collector = DataCollector()
    collector.load_drc_baseline()

    optimizer = ResourceOptimizationEngine()
    optimizer.load_drc_baseline()

    cs_engine = ConsumerSurplusEngine()
    cs_engine.load_baseline()

    ps_engine = ProducerSurplusEngine()
    ps_engine.load_baseline()

    resource_engine = NationalResourceEngine()
    resource_engine.load_baseline()

    gov_score = GovernanceScoreEngine()
    gov_score.load_baseline()

    corruption = CorruptionDetectionEngine()
    corruption.load_baseline()

    twin = NationalDigitalTwin()
    twin.load_baseline()

    decision = DecisionAI()

    return {
        "model": "IA GOV",
        "pipeline": "Collecte → Intelligence → Optimisation → Décision",
        "modules": {
            "optimizer": optimizer.get_dashboard(),
            "consumer_surplus": cs_engine.get_dashboard(),
            "producer_surplus": ps_engine.get_dashboard(),
            "resources": resource_engine.get_dashboard(),
            "governance_score": gov_score.get_dashboard(),
            "corruption": corruption.get_dashboard(),
            "digital_twin": twin.get_dashboard(),
            "decision_ai": decision.get_dashboard(),
        },
        "summary": {
            "national_welfare": round(optimizer.total_welfare, 2),
            "total_cs": round(cs_engine.total_cs, 2),
            "total_ps": round(ps_engine.total_ps, 2),
            "resource_value": round(resource_engine.total_gross_value, 2),
            "governance_score": gov_score.national_governance_score,
            "corruption_risk": round(corruption.total_amount_at_risk, 2),
            "provinces": len(twin.provinces),
        },
    }


# ── Module 1: Resource Optimization Engine ─────────────────────


@router.get("/optimizer")
def optimizer_dashboard(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    engine = ResourceOptimizationEngine()
    engine.load_drc_baseline()
    return engine.get_dashboard()


@router.post("/optimizer/simulate")
def simulate_policy(
    body: PolicySimulation,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission(Permission.BUDGET_WRITE)),
) -> dict:
    engine = ResourceOptimizationEngine()
    engine.load_drc_baseline()
    result = engine.simulate_policy(body.policy_name, body.sector_changes)
    record_audit_event(
        db,
        current_user,
        "policy_simulation.executed",
        "ia_gov_policy",
        body.policy_name,
        detail={"sector_changes": body.sector_changes},
    )
    return result


# ── Module 2: Consumer Surplus Engine ──────────────────────────


@router.get("/consumer-surplus")
def consumer_surplus_dashboard(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    engine = ConsumerSurplusEngine()
    engine.load_baseline()
    return engine.get_dashboard()


@router.get("/consumer-surplus/ranking")
def cs_ranking(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    engine = ConsumerSurplusEngine()
    engine.load_baseline()
    return {"services": engine.get_cs_ranking()}


# ── Module 3: Producer Surplus Engine ──────────────────────────


@router.get("/producer-surplus")
def producer_surplus_dashboard(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    engine = ProducerSurplusEngine()
    engine.load_baseline()
    return engine.get_dashboard()


@router.get("/producer-surplus/ranking")
def ps_ranking(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    engine = ProducerSurplusEngine()
    engine.load_baseline()
    return {"enterprises": engine.get_ps_ranking()}


@router.post("/producer-surplus/simulate-reform")
def simulate_reform(
    reform_name: str = Query("Réforme fiscale"),
    tax_reduction: float = Query(0.1),
    admin_reduction: float = Query(0.1),
    corruption_reduction: float = Query(0.1),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission(Permission.BUDGET_WRITE)),
) -> dict:
    engine = ProducerSurplusEngine()
    engine.load_baseline()
    result = engine.simulate_reform(reform_name, tax_reduction, admin_reduction, corruption_reduction)
    record_audit_event(
        db,
        current_user,
        "producer_reform_simulation.executed",
        "ia_gov_reform",
        reform_name,
        detail={
            "tax_reduction": tax_reduction,
            "admin_reduction": admin_reduction,
            "corruption_reduction": corruption_reduction,
        },
    )
    return result


# ── Module 4: National Resource Engine ─────────────────────────


@router.get("/resources")
def resources_dashboard(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    engine = NationalResourceEngine()
    engine.load_baseline()
    return engine.get_dashboard()


@router.get("/resources/mineral/{mineral}")
def mineral_breakdown(
    mineral: str,
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    engine = NationalResourceEngine()
    engine.load_baseline()
    breakdown = engine.get_mineral_breakdown()
    return {"mineral": mineral, "data": breakdown.get(mineral, {})}


# ── Module 5: Governance Score ─────────────────────────────────


@router.get("/governance")
def governance_dashboard(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    engine = GovernanceScoreEngine()
    engine.load_baseline()
    return engine.get_dashboard()


@router.get("/governance/ranking")
def governance_ranking(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    engine = GovernanceScoreEngine()
    engine.load_baseline()
    return {"ministries": engine.get_ranking()}


# ── Module 6: Corruption Detector ─────────────────────────────


@router.get("/corruption")
def corruption_dashboard(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    engine = CorruptionDetectionEngine()
    engine.load_baseline()
    return engine.get_dashboard()


@router.get("/corruption/risk-summary")
def corruption_risk_summary(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    engine = CorruptionDetectionEngine()
    engine.load_baseline()
    return engine.get_risk_summary()


# ── Module 7: National Digital Twin ───────────────────────────


@router.get("/twin")
def twin_dashboard(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    engine = NationalDigitalTwin()
    engine.load_baseline()
    return engine.get_dashboard()


@router.post("/twin/simulate")
def simulate_investment(
    body: InvestmentSimulation,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission(Permission.BUDGET_WRITE)),
) -> dict:
    engine = NationalDigitalTwin()
    engine.load_baseline()
    result = engine.simulate_investment(body.province, body.sector, body.amount)
    record_audit_event(
        db,
        current_user,
        "digital_twin_simulation.executed",
        "ia_gov_digital_twin",
        body.province,
        detail={"sector": body.sector, "amount": body.amount},
    )
    return result


@router.get("/twin/compare")
def compare_provinces(
    top_n: int = Query(5),
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    engine = NationalDigitalTwin()
    engine.load_baseline()
    return {"provinces": engine.compare_provinces(top_n)}


# ── Module 8: Decision AI ─────────────────────────────────────


@router.post("/decision")
def ask_decision(
    body: DecisionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission(Permission.INVESTMENT_OPTIMIZE)),
) -> dict:
    ai = DecisionAI()
    result = ai.answer(body.question, body.budget)
    record_audit_event(
        db,
        current_user,
        "decision_analysis.executed",
        "ia_gov_decision",
        "advisory",
        detail={"question": body.question, "budget": body.budget},
    )
    return result.to_dict()


@router.get("/decision/topics")
def decision_topics(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    ai = DecisionAI()
    return ai.get_dashboard()
