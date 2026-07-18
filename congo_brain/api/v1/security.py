"""PeaceNet API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from congo_brain.core.database import get_db
from congo_brain.schemas.security import SecurityAlertCreate, SecurityAlertOut
from congo_brain.services.security_service import SecurityService

router = APIRouter(prefix="/security", tags=["PeaceNet"])


def _svc(db: Session = Depends(get_db)) -> SecurityService:
    return SecurityService(db)


@router.get("/alerts")
def list_alerts(
    province: str | None = Query(None),
    severity: str | None = Query(None),
    active_only: bool = Query(False),
    svc: SecurityService = Depends(_svc),
) -> dict:
    alerts = svc.list_alerts(province, severity, active_only)
    return {"count": len(alerts), "alerts": [SecurityAlertOut.model_validate(a).model_dump() for a in alerts]}


@router.get("/dashboard")
def security_dashboard(svc: SecurityService = Depends(_svc)) -> dict:
    return svc.get_dashboard()


@router.post("/alerts", response_model=SecurityAlertOut, status_code=201)
def create_alert(body: SecurityAlertCreate, svc: SecurityService = Depends(_svc)) -> SecurityAlertOut:
    alert = svc.create_alert(**body.model_dump())
    return SecurityAlertOut.model_validate(alert)


@router.get("/alerts/{alert_id}", response_model=SecurityAlertOut)
def get_alert(alert_id: int, svc: SecurityService = Depends(_svc)) -> SecurityAlertOut:
    alert = svc.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Security alert not found")
    return SecurityAlertOut.model_validate(alert)


@router.post("/alerts/{alert_id}/resolve", response_model=SecurityAlertOut)
def resolve_alert(alert_id: int, svc: SecurityService = Depends(_svc)) -> SecurityAlertOut:
    alert = svc.resolve_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Security alert not found")
    return SecurityAlertOut.model_validate(alert)
