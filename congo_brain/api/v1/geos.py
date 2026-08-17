"""GEOS API — Government Economic Optimization System.

14 entity endpoints + unified SNN optimization.
Formula: max SNN = CS + PS + GR + NRV - DWL - EC
"""

from fastapi import APIRouter, HTTPException

from congo_brain.services.ia_gov.snn_engine import SNNOptimizationEngine

router = APIRouter(prefix="/geos", tags=["GEOS"])

_engine = SNNOptimizationEngine()


def _ensure_loaded() -> None:
    if not _engine.resources:
        _engine.load_drc_baseline()


# ── SNN Core ───────────────────────────────────────────────────

@router.get("/dashboard")
def dashboard() -> dict:
    """Vue complète du GEOS avec SNN agrégé."""
    _ensure_loaded()
    return _engine.get_dashboard()


@router.get("/snn")
def compute_snn() -> dict:
    """Calcule le SNN = CS + PS + GR + NRV - DWL - EC."""
    _ensure_loaded()
    return _engine.compute_snn().to_dict()


@router.post("/optimize")
def optimize(body: dict | None = None) -> dict:
    """Optimise l'allocation budgétaire pour max SNN."""
    _ensure_loaded()
    budget = (body or {}).get("budget", 10_000)
    return _engine.optimize_allocation(budget)


# ── Provinces ──────────────────────────────────────────────────

@router.get("/provinces")
def list_provinces() -> list[dict]:
    _ensure_loaded()
    return _engine.provinces


@router.get("/provinces/{name}")
def get_province(name: str) -> dict:
    _ensure_loaded()
    for p in _engine.provinces:
        if p.get("name", "").lower() == name.lower():
            return p
    raise HTTPException(status_code=404, detail=f"Province '{name}' not found")


# ── Companies ──────────────────────────────────────────────────

@router.get("/companies")
def list_companies() -> list[dict]:
    _ensure_loaded()
    return _engine.companies


@router.get("/companies/{name}")
def get_company(name: str) -> dict:
    _ensure_loaded()
    for c in _engine.companies:
        if c.get("name", "").lower() == name.lower():
            return c
    raise HTTPException(status_code=404, detail=f"Company '{name}' not found")


@router.get("/companies/ps/total")
def companies_ps_total() -> dict:
    """Total PS des entreprises."""
    _ensure_loaded()
    total = 0.0
    details = {}
    for c in _engine.companies:
        tc = (c.get("production_cost", 0) + c.get("tax_burden", 0)
              + c.get("admin_cost", 0) + c.get("corruption_cost", 0)
              + c.get("logistics_cost", 0) + c.get("energy_cost", 0))
        ps = max(0, c.get("revenue", 0) - tc)
        total += ps
        details[c["name"]] = round(ps, 2)
    return {"total_ps": round(total, 2), "details": details}


# ── Ministries ─────────────────────────────────────────────────

@router.get("/ministries")
def list_ministries() -> list[dict]:
    _ensure_loaded()
    return _engine.ministries


@router.get("/ministries/ranking")
def ministries_ranking() -> list[dict]:
    """Classement des ministères par score de gouvernance."""
    _ensure_loaded()
    ranking = []
    for m in _engine.ministries:
        gs = (0.40 * m.get("optimization_score", 0)
              + 0.20 * m.get("transparency_score", 0)
              + 0.20 * m.get("performance_score", 0)
              + 0.20 * m.get("satisfaction_score", 0))
        ranking.append({"name": m["name"], "governance_score": round(gs, 1)})
    ranking.sort(key=lambda x: x["governance_score"], reverse=True)
    return ranking


@router.get("/ministries/{name}")
def get_ministry(name: str) -> dict:
    _ensure_loaded()
    for m in _engine.ministries:
        if m.get("name", "").lower() == name.lower():
            gs = (0.40 * m.get("optimization_score", 0)
                  + 0.20 * m.get("transparency_score", 0)
                  + 0.20 * m.get("performance_score", 0)
                  + 0.20 * m.get("satisfaction_score", 0))
            exec_rate = round(m.get("budget_executed", 0) / m.get("budget_allocated", 1) * 100, 1)
            return {**m, "governance_score": round(gs, 1), "execution_rate": exec_rate}
    raise HTTPException(status_code=404, detail=f"Ministry '{name}' not found")
    return ranking


# ── Resources ──────────────────────────────────────────────────

@router.get("/resources")
def list_resources() -> list[dict]:
    _ensure_loaded()
    return _engine.resources


@router.get("/resources/{name}")
def get_resource(name: str) -> dict:
    _ensure_loaded()
    for r in _engine.resources:
        if r.get("name", "").lower() == name.lower():
            gv = r["annual_production_tons"] * r["market_value_per_ton"] / 1_000_000
            nrv = gv * (1 + r["local_processing_pct"] / 100)
            return {**r, "gross_value": round(gv, 2), "nrv": round(nrv, 2)}
    raise HTTPException(status_code=404, detail=f"Resource '{name}' not found")


@router.get("/resources/nrv/total")
def resources_nrv_total() -> dict:
    """Total NRV des ressources."""
    _ensure_loaded()
    total = 0.0
    details = {}
    for r in _engine.resources:
        gv = r["annual_production_tons"] * r["market_value_per_ton"] / 1_000_000
        nrv = gv * (1 + r["local_processing_pct"] / 100)
        total += nrv
        details[r["name"]] = round(nrv, 2)
    return {"total_nrv": round(total, 2), "details": details}


@router.get("/resources/ec/total")
def resources_ec_total() -> dict:
    """Total EC (coûts environnementaux)."""
    _ensure_loaded()
    total = sum(r.get("environmental_cost", 0) for r in _engine.resources)
    details = {r["name"]: r.get("environmental_cost", 0) for r in _engine.resources}
    return {"total_ec": round(total, 2), "details": details}


# ── Taxes ──────────────────────────────────────────────────────

@router.get("/taxes")
def list_taxes() -> list[dict]:
    _ensure_loaded()
    return _engine.taxes


@router.get("/taxes/revenue/total")
def taxes_revenue_total() -> dict:
    """Total GR (recettes publiques) des impôts."""
    _ensure_loaded()
    total = sum(t.get("revenue", 0) for t in _engine.taxes)
    evasion = sum(t.get("evasion_estimate", 0) for t in _engine.taxes)
    details = {t["name"]: {"revenue": t.get("revenue", 0), "evasion": t.get("evasion_estimate", 0)} for t in _engine.taxes}
    return {"total_revenue": round(total, 2), "total_evasion": round(evasion, 2), "details": details}


# ── Projects ───────────────────────────────────────────────────

@router.get("/projects")
def list_projects() -> list[dict]:
    _ensure_loaded()
    return _engine.projects


@router.get("/projects/snn/total")
def projects_snn_total() -> dict:
    """Impact SNN total des projets."""
    _ensure_loaded()
    total = 0.0
    details = {}
    for p in _engine.projects:
        snn = (p.get("cs_impact", 0) + p.get("ps_impact", 0)
               + p.get("gr_impact", 0) + p.get("nrv_impact", 0)
               - p.get("dwl_impact", 0) - p.get("ec_impact", 0))
        total += snn
        details[p["name"]] = round(snn, 2)
    return {"total_snn": round(total, 2), "details": details}


# ── Public Services ────────────────────────────────────────────

@router.get("/public-services")
def list_public_services() -> list[dict]:
    _ensure_loaded()
    return _engine.public_services


@router.get("/public-services/cs/total")
def public_services_cs_total() -> dict:
    """Total CS (consumer surplus) des services publics."""
    _ensure_loaded()
    total = 0.0
    details = {}
    for ps in _engine.public_services:
        cs = max(0, ps.get("willingness_to_pay", 0) - ps.get("actual_price", 0) - ps.get("indirect_cost", 0))
        qa = cs * (ps.get("quality_score", 0) / 10) if ps.get("quality_score", 0) > 0 else 0
        total += qa
        details[ps["name"]] = round(qa, 2)
    return {"total_cs": round(total, 2), "details": details}


# ── Contracts ──────────────────────────────────────────────────

@router.get("/contracts")
def list_contracts() -> list[dict]:
    _ensure_loaded()
    return _engine.contracts


# ── Payments ───────────────────────────────────────────────────

@router.get("/payments")
def list_payments() -> list[dict]:
    _ensure_loaded()
    return _engine.payments


# ── Markets ────────────────────────────────────────────────────

@router.get("/markets")
def list_markets() -> list[dict]:
    _ensure_loaded()
    return _engine.markets


# ── Indicators ─────────────────────────────────────────────────

@router.get("/indicators")
def list_indicators() -> list[dict]:
    _ensure_loaded()
    return _engine.indicators
