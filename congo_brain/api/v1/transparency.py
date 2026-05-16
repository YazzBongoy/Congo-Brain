"""TranspaFin API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from congo_brain.core.database import get_db
from congo_brain.schemas.transparency import TransparencyReportCreate, TransparencyReportOut
from congo_brain.services.transparency_service import TransparencyService

router = APIRouter(prefix="/transparency", tags=["TranspaFin"])


def _svc(db: Session = Depends(get_db)) -> TransparencyService:
    return TransparencyService(db)


@router.get("")
def list_reports(
    ministry: str | None = Query(None),
    status: str | None = Query(None),
    svc: TransparencyService = Depends(_svc),
) -> dict:
    reports = svc.list_reports(ministry, status)
    return {"count": len(reports), "reports": [TransparencyReportOut.model_validate(r).model_dump() for r in reports]}


@router.get("/dashboard")
def transparency_dashboard(svc: TransparencyService = Depends(_svc)) -> dict:
    return svc.get_dashboard()


@router.post("", response_model=TransparencyReportOut, status_code=201)
def create_report(body: TransparencyReportCreate, svc: TransparencyService = Depends(_svc)) -> TransparencyReportOut:
    report = svc.create_report(**body.model_dump())
    return TransparencyReportOut.model_validate(report)


@router.get("/{report_id}", response_model=TransparencyReportOut)
def get_report(report_id: int, svc: TransparencyService = Depends(_svc)) -> TransparencyReportOut:
    report = svc.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Transparency report not found")
    return TransparencyReportOut.model_validate(report)
