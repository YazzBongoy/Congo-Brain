"""MOEG Economic Engine API — Surplus National Net (SNN) endpoints.

SNN = CS + PS + GR + NRV - DWL - EC

Provides:
    /api/v1/economic/welfare       — SNN welfare model dashboard
    /api/v1/economic/resources     — Natural resource NRV optimizer
    /api/v1/economic/investments   — Investment allocation (NSB scoring)
    /api/v1/economic/nwi           — National Welfare Index
    /api/v1/economic/corruption    — DWL + EC cost calculator
    /api/v1/economic/dashboard     — Combined MOEG SNN dashboard
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
from congo_brain.services.economic.corruption_calculator import CorruptionCalculator, DWLComponents, EnvironmentalCost

router = APIRouter(prefix="/economic", tags=["MOEG"])


class SectorInput(BaseModel):
    sector: str
    cs: float
    ps: float
    revenue: float
    nrv: float = 0.0
    dwl: float = 0.0
    ec: float = 0.0


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
    natural_resource_value: float = 0.0
    sustainability: float
    dwl_rate: float = 0.0
    ec_rate: float = 0.0
    max_cs: float = 10.0
    max_ps: float = 10.0
    max_revenue: float = 10.0
    max_nrv: float = 10.0
    max_sustainability: float = 10.0


class InvestmentWeights(BaseModel):
    w_revenue: float = 0.15
    w_jobs: float = 0.20
    w_nrv: float = 0.20
    w_sustainability: float = 0.05
    w_cost: float = 0.15
    w_corruption: float = 0.15
    w_env: float = 0.10
    w_duration: float = 0.05


# ── Welfare Model (SNN) ───────────────────────────────────────

@router.get("/welfare")
def welfare_dashboard(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    wm = WelfareModel()
    wm.add_sector("Énergie", cs=4.5, ps=5.0, revenue=2.0, nrv=3.0, dwl=1.2, ec=0.8)
    wm.add_sector("Transport", cs=3.0, ps=4.0, revenue=1.5, nrv=1.0, dwl=0.8, ec=0.5)
    wm.add_sector("Santé", cs=6.0, ps=1.0, revenue=0.5, nrv=0.2, dwl=0.3, ec=0.1)
    wm.add_sector("Industrie minière", cs=2.0, ps=6.5, revenue=3.0, nrv=8.0, dwl=1.5, ec=1.2)
    wm.add_sector("Agriculture", cs=5.0, ps=3.0, revenue=1.0, nrv=2.0, dwl=0.5, ec=0.3)
    wm.add_sector("Forêt", cs=3.5, ps=2.0, revenue=0.8, nrv=4.0, dwl=0.4, ec=1.5)
    wm.add_sector("Numérique", cs=3.5, ps=4.5, revenue=1.8, nrv=0.5, dwl=0.4, ec=0.1)
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
    sw = wm.add_sector(body.sector, body.cs, body.ps, body.revenue, body.nrv, body.dwl, body.ec)
    return sw.to_dict()


# ── Resources (NRV) ───────────────────────────────────────────

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
        "nrv_total": round(ro.total_nrv, 2),
        "recommendations": ro.get_optimization_recommendations(),
    }


# ── Investment Allocation (NSB) ───────────────────────────────

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


# ── National Welfare Index (SNN-aligned) ──────────────────────

@router.get("/nwi")
def nwi_dashboard(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    nwi = NationalWelfareIndex()
    sectors = {
        "Énergie": NWIComponents(6.0, 7.0, 3.0, 5.0, 5.0, 15.0, 10.0, 10.0, 10.0, 10.0, 10.0),
        "Industrie minière": NWIComponents(3.0, 8.0, 5.0, 9.0, 3.0, 20.0, 15.0, 10.0, 10.0, 10.0, 10.0),
        "Santé": NWIComponents(7.0, 2.0, 1.0, 0.5, 6.0, 5.0, 3.0, 10.0, 10.0, 10.0, 10.0),
        "Agriculture": NWIComponents(6.5, 4.0, 1.5, 3.0, 7.0, 8.0, 5.0, 10.0, 10.0, 10.0, 10.0),
        "Forêt": NWIComponents(4.0, 2.5, 0.8, 5.0, 8.0, 6.0, 20.0, 10.0, 10.0, 10.0, 10.0),
        "Éducation": NWIComponents(7.5, 5.0, 1.0, 0.5, 8.0, 3.0, 2.0, 10.0, 10.0, 10.0, 10.0),
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
        natural_resource_value=body.natural_resource_value,
        sustainability=body.sustainability,
        dwl_rate=body.dwl_rate,
        ec_rate=body.ec_rate,
        max_cs=body.max_cs,
        max_ps=body.max_ps,
        max_revenue=body.max_revenue,
        max_nrv=body.max_nrv,
        max_sustainability=body.max_sustainability,
    )
    return nwi.compute_nwi(comp)


# ── Corruption + Environmental Cost ───────────────────────────

@router.get("/corruption")
def corruption_dashboard(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    cc = CorruptionCalculator()
    return cc.get_dashboard()


@router.get("/corruption/scenarios")
def corruption_scenarios(
    dwl_reduction: float = Query(25.0, description="DWL reduction percentage"),
    ec_reduction: float = Query(25.0, description="Environmental cost reduction percentage"),
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    cc = CorruptionCalculator()
    return cc.scenario_analysis(dwl_reduction, ec_reduction)


# ── Combined MOEG SNN Dashboard ──────────────────────────────

@router.get("/dashboard")
def moeg_dashboard(
    budget: float = Query(10000, description="Budget in millions USD"),
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    wm = WelfareModel()
    wm.add_sector("Énergie", 4.5, 5.0, 2.0, 3.0, 1.2, 0.8)
    wm.add_sector("Industrie minière", 2.0, 6.5, 3.0, 8.0, 1.5, 1.2)
    wm.add_sector("Agriculture", 5.0, 3.0, 1.0, 2.0, 0.5, 0.3)
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
    nwi.add_sector("Énergie", NWIComponents(6.0, 7.0, 3.0, 5.0, 5.0, 15.0, 10.0))
    nwi.add_sector("Industrie", NWIComponents(3.0, 8.0, 5.0, 9.0, 3.0, 20.0, 15.0))
    nwi.add_sector("Santé", NWIComponents(7.0, 2.0, 1.0, 0.5, 6.0, 5.0, 3.0))

    cc = CorruptionCalculator()

    return {
        "model": "MOEG",
        "description": "Modele d'Optimisation Economique de la Gouvernance — Surplus National Net",
        "formula": "SNN = CS + PS + GR + NRV - DWL - EC",
        "welfare": wm.get_dashboard(),
        "resources": ro.get_dashboard(),
        "investments": ia.optimize(),
        "nwi": nwi.compute_nwi(),
        "corruption": cc.get_dashboard(),
    }
