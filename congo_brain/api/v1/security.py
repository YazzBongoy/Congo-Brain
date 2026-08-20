"""PeaceNet API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from congo_brain.core.database import get_db
from congo_brain.core.rbac import Permission
from congo_brain.core.security import require_permission
from congo_brain.schemas.security import SecurityAlertCreate, SecurityAlertOut
from congo_brain.services.audit_service import record_audit_event
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
    _user: dict = Depends(require_permission(Permission.SECURITY_READ)),
) -> dict:
    alerts = svc.list_alerts(province, severity, active_only)
    return {"count": len(alerts), "alerts": [SecurityAlertOut.model_validate(a).model_dump() for a in alerts]}


@router.get("/dashboard")
def security_dashboard(
    svc: SecurityService = Depends(_svc),
    _user: dict = Depends(require_permission(Permission.SECURITY_READ)),
) -> dict:
    return svc.get_dashboard()


@router.get("/trends")
def security_trends(
    group_by: str = Query("month", description="Time grouping: 'month' or 'week'"),
    svc: SecurityService = Depends(_svc),
    _user: dict = Depends(require_permission(Permission.SECURITY_READ)),
) -> dict:
    """Get risk trends over time."""
    return svc.get_trends(group_by=group_by)


@router.get("/compare")
def compare_provinces(
    top_n: int = Query(5, description="Number of top provinces to compare"),
    svc: SecurityService = Depends(_svc),
    _user: dict = Depends(require_permission(Permission.SECURITY_READ)),
) -> dict:
    """Compare risk levels across provinces."""
    return svc.compare_provinces(top_n=top_n)


@router.post("/alerts", response_model=SecurityAlertOut, status_code=201)
def create_alert(
    body: SecurityAlertCreate,
    db: Session = Depends(get_db),
    svc: SecurityService = Depends(_svc),
    current_user: dict = Depends(require_permission(Permission.SECURITY_WRITE)),
) -> SecurityAlertOut:
    alert = svc.create_alert(commit=False, **body.model_dump())
    record_audit_event(
        db,
        current_user,
        "security_alert.created",
        "security_alert",
        alert.id,
        detail={"province": alert.province, "severity": alert.severity},
    )
    return SecurityAlertOut.model_validate(alert)


@router.get("/alerts/{alert_id}", response_model=SecurityAlertOut)
def get_alert(
    alert_id: int,
    svc: SecurityService = Depends(_svc),
    _user: dict = Depends(require_permission(Permission.SECURITY_READ)),
) -> SecurityAlertOut:
    alert = svc.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Security alert not found")
    return SecurityAlertOut.model_validate(alert)


@router.post("/alerts/{alert_id}/resolve", response_model=SecurityAlertOut)
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    svc: SecurityService = Depends(_svc),
    current_user: dict = Depends(require_permission(Permission.SECURITY_RESOLVE)),
) -> SecurityAlertOut:
    alert = svc.resolve_alert(alert_id, commit=False)
    if not alert:
        raise HTTPException(status_code=404, detail="Security alert not found")
    record_audit_event(
        db,
        current_user,
        "security_alert.resolved",
        "security_alert",
        alert.id,
        detail={"province": alert.province, "severity": alert.severity},
    )
    return SecurityAlertOut.model_validate(alert)
