"""MOEG Economic Engine API — Endpoints for welfare optimization.

Provides:
    /api/v1/economic/welfare       — Welfare model dashboard
    /api/v1/economic/resources     — Natural resource optimizer
    /api/v1/economic/investments   — Investment allocation (LP)
    /api/v1/economic/nwi           — National Welfare Index
    /api/v1/economic/corruption    — DWL calculator
    /api/v1/economic/dashboard     — Combined MOEG dashboard
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from congo_brain.core.rbac import Permission
from congo_brain.core.security import require_permission
from congo_brain.services.economic.welfare_model import WelfareModel, EconomyConstraints
from congo_brain.services.economic.resource_optimizer import ResourceOptimizer
from congo_brain.services.economic.investment_allocator import InvestmentAllocator
from congo_brain.services.economic.nwi import NationalWelfareIndex, NWIComponents
from congo_brain.services.economic.corruption_calculator import CorruptionCalculator, DWLComponents

router = APIRouter(prefix="/economic", tags=["MOEG"])


class SectorInput(BaseModel):
    sector: str
    cs: float
    ps: float
    revenue: float
    dwl: float


class ConstraintInput(BaseModel):
    budget_ceiling: float = 10.0
    revenue: float = 8.5
    current_debt_to_gdp: float = 45.0
    max_debt_to_gdp: float = 60.0
    current_inflation: float = 3.0
    max_inflation: float = 5.0
    gdp: float = 55.0


class NWIInput(BaseModel):
    consumer_surplus: float
    producer_surplus: float
    government_revenue: float
    sustainability: float
    max_cs: float = 10.0
    max_ps: float = 10.0
    max_revenue: float = 10.0
    max_sustainability: float = 10.0


class InvestmentWeights(BaseModel):
    w_cs: float = 0.25
    w_ps: float = 0.25
    w_jobs: float = 0.20
    w_gdp: float = 0.15
    w_corruption: float = 0.10
    w_sustainability: float = 0.05


# ── Welfare Model ──────────────────────────────────────────────

@router.get("/welfare")
def welfare_dashboard(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    wm = WelfareModel()
    wm.add_sector("Énergie", cs=4.5, ps=5.0, revenue=2.0, dwl=1.2)
    wm.add_sector("Transport", cs=3.0, ps=4.0, revenue=1.5, dwl=0.8)
    wm.add_sector("Santé", cs=6.0, ps=1.0, revenue=0.5, dwl=0.3)
    wm.add_sector("Industrie", cs=2.0, ps=6.5, revenue=3.0, dwl=1.5)
    wm.add_sector("Agriculture", cs=5.0, ps=3.0, revenue=1.0, dwl=0.5)
    wm.add_sector("Numérique", cs=3.5, ps=4.5, revenue=1.8, dwl=0.4)
    wm.set_constraints(EconomyConstraints(
        budget_ceiling=10.0, revenue=8.5,
        current_debt_to_gdp=45.0, gdp=55.0, current_inflation=3.0,
    ))
    return wm.get_dashboard()


@router.post("/welfare/sectors")
def add_sector(
    body: SectorInput,
    _user: dict = Depends(require_permission(Permission.BUDGET_WRITE)),
) -> dict:
    wm = WelfareModel()
    sw = wm.add_sector(body.sector, body.cs, body.ps, body.revenue, body.dwl)
    return sw.to_dict()


# ── Resources ──────────────────────────────────────────────────

@router.get("/resources")
def resources_dashboard(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    ro = ResourceOptimizer()
    ro.load_baseline()
    return ro.get_dashboard()


@router.get("/resources/recommendations")
def resource_recommendations(
    target_capture: float = Query(40.0, description="Target local capture rate (%)"),
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    ro = ResourceOptimizer()
    ro.load_baseline()
    ro.set_target_capture_rate(target_capture)
    return {
        "target_capture_rate": target_capture,
        "recommendations": ro.get_optimization_recommendations(),
    }


# ── Investment Allocation ─────────────────────────────────────

@router.get("/investments")
def investments_dashboard(
    budget: float = Query(10000, description="Budget in millions USD"),
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    ia = InvestmentAllocator()
    ia.load_baseline()
    ia.set_budget(budget)
    return ia.get_dashboard()


@router.post("/investments/optimize")
def optimize_investments(
    budget: float = Query(10000, description="Budget in millions USD"),
    weights: InvestmentWeights | None = None,
    _user: dict = Depends(require_permission(Permission.BUDGET_WRITE)),
) -> dict:
    ia = InvestmentAllocator()
    ia.load_baseline()
    ia.set_budget(budget)
    w = weights.model_dump() if weights else None
    return ia.optimize(w)


@router.post("/investments/scenarios")
def investment_scenarios(
    budgets: list[float] = Query([5000, 10000, 20000], description="Budget levels to compare"),
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    ia = InvestmentAllocator()
    ia.load_baseline()
    scenarios = ia.compare_scenarios(budgets)
    return {"budgets": budgets, "scenarios": scenarios}


@router.get("/investments/rankings")
def investment_rankings(
    weights: InvestmentWeights | None = None,
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    ia = InvestmentAllocator()
    ia.load_baseline()
    w = weights.model_dump() if weights else None
    return {"projects": ia.get_project_scores(w)}


# ── National Welfare Index ────────────────────────────────────

@router.get("/nwi")
def nwi_dashboard(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    nwi = NationalWelfareIndex()
    sectors = {
        "Énergie": NWIComponents(6.0, 7.0, 3.0, 5.0, 10.0, 10.0, 10.0, 10.0),
        "Transport": NWIComponents(5.0, 6.0, 2.5, 4.0, 10.0, 10.0, 10.0, 10.0),
        "Santé": NWIComponents(7.0, 2.0, 1.0, 6.0, 10.0, 10.0, 10.0, 10.0),
        "Industrie": NWIComponents(3.0, 8.0, 5.0, 3.0, 10.0, 10.0, 10.0, 10.0),
        "Agriculture": NWIComponents(6.5, 4.0, 1.5, 7.0, 10.0, 10.0, 10.0, 10.0),
        "Éducation": NWIComponents(7.5, 5.0, 1.0, 8.0, 10.0, 10.0, 10.0, 10.0),
    }
    for name, comp in sectors.items():
        nwi.add_sector(name, comp)
    return nwi.get_dashboard()


@router.post("/nwi/compute")
def compute_nwi(
    body: NWIInput,
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    nwi = NationalWelfareIndex()
    comp = NWIComponents(
        consumer_surplus=body.consumer_surplus,
        producer_surplus=body.producer_surplus,
        government_revenue=body.government_revenue,
        sustainability=body.sustainability,
        max_cs=body.max_cs,
        max_ps=body.max_ps,
        max_revenue=body.max_revenue,
        max_sustainability=body.max_sustainability,
    )
    return nwi.compute_nwi(comp)


# ── Corruption / DWL ──────────────────────────────────────────

@router.get("/corruption")
def corruption_dashboard(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    cc = CorruptionCalculator()
    return cc.get_dashboard()


@router.get("/corruption/scenarios")
def corruption_scenarios(
    reduction_pct: float = Query(25.0, description="DWL reduction percentage"),
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    cc = CorruptionCalculator()
    return cc.scenario_analysis(reduction_pct)


# ── Combined MOEG Dashboard ───────────────────────────────────

@router.get("/dashboard")
def moeg_dashboard(
    budget: float = Query(10000, description="Budget in millions USD"),
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    wm = WelfareModel()
    wm.add_sector("Énergie", 4.5, 5.0, 2.0, 1.2)
    wm.add_sector("Transport", 3.0, 4.0, 1.5, 0.8)
    wm.add_sector("Santé", 6.0, 1.0, 0.5, 0.3)
    wm.add_sector("Industrie", 2.0, 6.5, 3.0, 1.5)
    wm.add_sector("Agriculture", 5.0, 3.0, 1.0, 0.5)
    wm.set_constraints(EconomyConstraints(
        budget_ceiling=10.0, revenue=8.5,
        current_debt_to_gdp=45.0, gdp=55.0, current_inflation=3.0,
    ))

    ro = ResourceOptimizer()
    ro.load_baseline()

    ia = InvestmentAllocator()
    ia.load_baseline()
    ia.set_budget(budget)

    nwi = NationalWelfareIndex()
    nwi.add_sector("Énergie", NWIComponents(6.0, 7.0, 3.0, 5.0))
    nwi.add_sector("Industrie", NWIComponents(3.0, 8.0, 5.0, 3.0))
    nwi.add_sector("Santé", NWIComponents(7.0, 2.0, 1.0, 6.0))

    cc = CorruptionCalculator()

    return {
        "model": "MOEG",
        "description": "Modele d'Optimisation Economique de la Gouvernance",
        "welfare": wm.get_dashboard(),
        "resources": ro.get_dashboard(),
        "investments": ia.optimize(),
        "nwi": nwi.compute_nwi(),
        "corruption": cc.get_dashboard(),
    }
