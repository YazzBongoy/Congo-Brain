"""BudgetGuard API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from congo_brain.core.database import get_db
from congo_brain.schemas.budget import BudgetCreate, BudgetOut, BudgetStatusOut, TransactionCreate, TransactionOut
from congo_brain.services.budget_service import BudgetService

router = APIRouter(prefix="/budgets", tags=["BudgetGuard"])


def _svc(db: Session = Depends(get_db)) -> BudgetService:
    return BudgetService(db)


@router.get("", response_model=dict)
def list_budgets(
    ministry: str | None = Query(None),
    fiscal_year: int | None = Query(None),
    svc: BudgetService = Depends(_svc),
) -> dict:
    budgets = svc.list_budgets(ministry, fiscal_year)
    return {"count": len(budgets), "budgets": [BudgetOut.model_validate(b).model_dump() for b in budgets]}


@router.get("/status", response_model=BudgetStatusOut)
def budget_status(svc: BudgetService = Depends(_svc)) -> dict:
    return svc.get_status()


@router.get("/anomalies")
def detect_anomalies(svc: BudgetService = Depends(_svc)) -> dict:
    report = svc.run_anomaly_detection()
    report["anomalies"] = [TransactionOut.model_validate(t).model_dump() for t in report["anomalies"]]
    return report


@router.get("/summary")
def ministry_summary(svc: BudgetService = Depends(_svc)) -> dict:
    return {"summary": svc.get_ministry_summary()}


@router.post("", response_model=BudgetOut, status_code=201)
def create_budget(body: BudgetCreate, svc: BudgetService = Depends(_svc)) -> BudgetOut:
    b = svc.create_budget(body.ministry, body.sector, body.allocated_amount, body.fiscal_year, body.spent_amount)
    return BudgetOut.model_validate(b)


@router.get("/{budget_id}", response_model=BudgetOut)
def get_budget(budget_id: int, svc: BudgetService = Depends(_svc)) -> BudgetOut:
    b = svc.get_budget(budget_id)
    if not b:
        raise HTTPException(status_code=404, detail="Budget not found")
    return BudgetOut.model_validate(b)


@router.get("/{budget_id}/transactions")
def list_transactions(budget_id: int, svc: BudgetService = Depends(_svc)) -> dict:
    txns = svc.list_transactions(budget_id)
    return {"count": len(txns), "transactions": [TransactionOut.model_validate(t).model_dump() for t in txns]}


@router.post("/{budget_id}/transactions", response_model=TransactionOut, status_code=201)
def create_transaction(budget_id: int, body: TransactionCreate, svc: BudgetService = Depends(_svc)) -> TransactionOut:
    if body.budget_id != budget_id:
        raise HTTPException(status_code=400, detail="budget_id in body must match URL")
    t = svc.create_transaction(
        body.budget_id, body.amount, body.description,
        body.transaction_type, body.reference_number, body.beneficiary,
    )
    return TransactionOut.model_validate(t)
