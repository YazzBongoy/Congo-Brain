"""TranspaFin API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from congo_brain.core.database import get_db
from congo_brain.core.rbac import Permission
from congo_brain.core.security import enforce_ministry_access, require_permission, resolve_ministry_scope
from congo_brain.schemas.transparency import TransparencyReportCreate, TransparencyReportOut
from congo_brain.services.audit_service import record_audit_event
from congo_brain.services.transparency_service import TransparencyService

router = APIRouter(prefix="/transparency", tags=["TranspaFin"])


def _svc(db: Session = Depends(get_db)) -> TransparencyService:
    return TransparencyService(db)


@router.get("")
def list_reports(
    ministry: str | None = Query(None),
    status: str | None = Query(None),
    svc: TransparencyService = Depends(_svc),
    current_user: dict = Depends(require_permission(Permission.TRANSPARENCY_READ)),
) -> dict:
    ministry = resolve_ministry_scope(current_user, ministry)
    reports = svc.list_reports(ministry, status)
    return {"count": len(reports), "reports": [TransparencyReportOut.model_validate(r).model_dump() for r in reports]}


@router.get("/dashboard")
def transparency_dashboard(
    svc: TransparencyService = Depends(_svc),
    current_user: dict = Depends(require_permission(Permission.TRANSPARENCY_READ)),
) -> dict:
    return svc.get_dashboard(resolve_ministry_scope(current_user))


@router.post("", response_model=TransparencyReportOut, status_code=201)
def create_report(
    body: TransparencyReportCreate,
    db: Session = Depends(get_db),
    svc: TransparencyService = Depends(_svc),
    current_user: dict = Depends(require_permission(Permission.TRANSPARENCY_WRITE)),
) -> TransparencyReportOut:
    enforce_ministry_access(current_user, body.ministry)
    report = svc.create_report(**body.model_dump())
    record_audit_event(
        db,
        current_user,
        "transparency_report.created",
        "transparency_report",
        report.id,
        ministry=report.ministry,
        detail={"period": report.period, "status": report.status},
    )
    return TransparencyReportOut.model_validate(report)


@router.get("/{report_id}", response_model=TransparencyReportOut)
def get_report(
    report_id: int,
    svc: TransparencyService = Depends(_svc),
    current_user: dict = Depends(require_permission(Permission.TRANSPARENCY_READ)),
) -> TransparencyReportOut:
    report = svc.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Transparency report not found")
    enforce_ministry_access(current_user, report.ministry)
    return TransparencyReportOut.model_validate(report)
