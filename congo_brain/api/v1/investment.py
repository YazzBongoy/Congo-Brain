"""InvestSmart API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from congo_brain.core.database import get_db
from congo_brain.core.security import get_current_user, require_role
from congo_brain.schemas.investment import InvestmentCreate, InvestmentOut
from congo_brain.services.investment_service import InvestmentService

router = APIRouter(prefix="/investments", tags=["InvestSmart"])


def _svc(db: Session = Depends(get_db)) -> InvestmentService:
    return InvestmentService(db)


@router.get("")
def list_investments(
    status: str | None = Query(None),
    province: str | None = Query(None),
    sector: str | None = Query(None),
    svc: InvestmentService = Depends(_svc),
    _user: dict = Depends(get_current_user),
) -> dict:
    invs = svc.list_investments(status, province, sector)
    return {"count": len(invs), "investments": [InvestmentOut.model_validate(i).model_dump() for i in invs]}


@router.get("/optimize")
def optimize_portfolio(
    budget: float = Query(..., description="Budget limit in FC"),
    svc: InvestmentService = Depends(_svc),
    _user: dict = Depends(get_current_user),
) -> dict:
    result = svc.optimize(budget)
    result["selected_projects"] = [InvestmentOut.model_validate(p).model_dump() for p in result["selected_projects"]]
    result["projects_excluded"] = [InvestmentOut.model_validate(p).model_dump() for p in result["projects_excluded"]]
    return result


@router.get("/summary")
def investment_summary(
    svc: InvestmentService = Depends(_svc),
    _user: dict = Depends(get_current_user),
) -> dict:
    return svc.get_summary()


@router.post("", response_model=InvestmentOut, status_code=201)
def create_investment(
    body: InvestmentCreate,
    svc: InvestmentService = Depends(_svc),
    _user: dict = Depends(require_role("admin", "analyst")),
) -> InvestmentOut:
    inv = svc.create_investment(**body.model_dump())
    return InvestmentOut.model_validate(inv)


@router.get("/{inv_id}", response_model=InvestmentOut)
def get_investment(
    inv_id: int,
    svc: InvestmentService = Depends(_svc),
    _user: dict = Depends(get_current_user),
) -> InvestmentOut:
    inv = svc.get_investment(inv_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investment not found")
    return InvestmentOut.model_validate(inv)
