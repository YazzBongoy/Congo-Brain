"""IA GOV API — Intelligence Artificielle pour la Gouvernance.

Pipeline: Collecte → Intelligence → Optimisation → Dashboard → Décision

Endpoints:
    /api/v1/ia-gov/dashboard       — Tableau de bord complet
    /api/v1/ia-gov/welfare         — État du Surplus National Net
    /api/v1/ia-gov/sectors         — Analyse sectorielle CS/PS/GR
    /api/v1/ia-gov/decisions       — Support décisionnel + optimisation
    /api/v1/ia-gov/alerts          — Alertes de gouvernance
    /api/v1/ia-gov/recommendations — Recommandations d'optimisation
    /api/v1/ia-gov/historical      — Tendances historiques
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from congo_brain.core.rbac import Permission
from congo_brain.core.security import require_permission
from congo_brain.services.ia_gov.dashboard import GovDashboard

router = APIRouter(prefix="/ia-gov", tags=["IA GOV"])


def _dashboard() -> GovDashboard:
    return GovDashboard()


@router.get("/dashboard")
def ia_gov_dashboard(
    budget: float = Query(10_000, description="Budget d'investissement (M USD)"),
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    """Tableau de bord complet IA GOV — pipeline complet."""
    return _dashboard().run_full_analysis(budget)


@router.get("/welfare")
def welfare_status(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    """État du Surplus National Net national."""
    return _dashboard().get_welfare_status()


@router.get("/sectors")
def sector_analysis(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    """Analyse sectorielle détaillée: CS, PS, GR, NRV, DWL, EC."""
    sectors = _dashboard().get_sector_analysis()
    return {"sector_count": len(sectors), "sectors": sectors}


@router.get("/decisions")
def decision_support(
    budget: float = Query(10_000, description="Budget d'investissement (M USD)"),
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    """Support décisionnel: allocation optimale + scénarios + sensibilité."""
    return _dashboard().get_decision_support(budget)


@router.get("/alerts")
def governance_alerts(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    """Alertes de gouvernance basées sur les données."""
    alerts = _dashboard().get_alerts()
    return {
        "count": len(alerts),
        "critical": len([a for a in alerts if a["level"] == "critique"]),
        "alerts": alerts,
    }


@router.get("/recommendations")
def recommendations(
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    """Recommandations d'optimisation basées sur l'analyse SNN."""
    recs = _dashboard().get_recommendations()
    return {"count": len(recs), "recommendations": recs}


@router.get("/historical")
def historical_trends(
    years: int = Query(5, description="Nombre d'années historiques"),
    _user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    """Tendances historiques (PIB, pauvreté, électricité, etc.)."""
    data = _dashboard().get_historical(years)
    return {"years": len(data), "data": data}
