"""BudgetGuard API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from congo_brain.core.database import get_db
from congo_brain.core.rbac import Permission
from congo_brain.core.security import enforce_ministry_access, require_permission, resolve_ministry_scope
from congo_brain.schemas.budget import BudgetCreate, BudgetOut, BudgetStatusOut, TransactionCreate, TransactionOut
from congo_brain.services.audit_service import record_audit_event
from congo_brain.services.budget_service import BudgetService

router = APIRouter(prefix="/budgets", tags=["BudgetGuard"])


def _svc(db: Session = Depends(get_db)) -> BudgetService:
    return BudgetService(db)


@router.get("", response_model=dict)
def list_budgets(
    ministry: str | None = Query(None),
    fiscal_year: int | None = Query(None),
    svc: BudgetService = Depends(_svc),
    current_user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    ministry = resolve_ministry_scope(current_user, ministry)
    budgets = svc.list_budgets(ministry, fiscal_year)
    return {"count": len(budgets), "budgets": [BudgetOut.model_validate(b).model_dump() for b in budgets]}


@router.get("/status", response_model=BudgetStatusOut)
def budget_status(
    svc: BudgetService = Depends(_svc),
    current_user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    return svc.get_status(resolve_ministry_scope(current_user))


@router.get("/anomalies")
def detect_anomalies(
    db: Session = Depends(get_db),
    svc: BudgetService = Depends(_svc),
    current_user: dict = Depends(require_permission(Permission.BUDGET_WRITE)),
) -> dict:
    report = svc.run_anomaly_detection(resolve_ministry_scope(current_user), commit=False)
    report["anomalies"] = [TransactionOut.model_validate(t).model_dump() for t in report["anomalies"]]
    record_audit_event(
        db,
        current_user,
        "budget_anomaly_detection.executed",
        "budget_anomaly_detection",
        "scan",
        ministry=resolve_ministry_scope(current_user),
        detail={"anomalies_detected": report["anomalies_detected"]},
    )
    return report


@router.get("/anomalies/summary")
def anomaly_summary(
    threshold: float = Query(2.0, description="Z-score threshold"),
    db: Session = Depends(get_db),
    svc: BudgetService = Depends(_svc),
    current_user: dict = Depends(require_permission(Permission.BUDGET_WRITE)),
) -> dict:
    """Get anomaly detection summary with severity classification."""
    result = svc.run_anomaly_detection_enhanced(
        threshold=threshold,
        ministry=resolve_ministry_scope(current_user),
        commit=False,
    )
    record_audit_event(
        db,
        current_user,
        "budget_anomaly_summary.executed",
        "budget_anomaly_detection",
        "summary",
        ministry=resolve_ministry_scope(current_user),
        detail={"threshold": threshold, "anomalies_detected": result["anomalies_detected"]},
    )
    return result


@router.get("/summary")
def ministry_summary(
    svc: BudgetService = Depends(_svc),
    current_user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    return {"summary": svc.get_ministry_summary(resolve_ministry_scope(current_user))}


@router.post("", response_model=BudgetOut, status_code=201)
def create_budget(
    body: BudgetCreate,
    db: Session = Depends(get_db),
    svc: BudgetService = Depends(_svc),
    current_user: dict = Depends(require_permission(Permission.BUDGET_WRITE)),
) -> BudgetOut:
    enforce_ministry_access(current_user, body.ministry)
    budget = svc.create_budget(
        body.ministry,
        body.sector,
        body.allocated_amount,
        body.fiscal_year,
        body.spent_amount,
        commit=False,
    )
    record_audit_event(
        db,
        current_user,
        "budget.created",
        "budget",
        budget.id,
        ministry=budget.ministry,
        detail={"sector": budget.sector, "fiscal_year": budget.fiscal_year},
    )
    return BudgetOut.model_validate(budget)


@router.get("/{budget_id}", response_model=BudgetOut)
def get_budget(
    budget_id: int,
    svc: BudgetService = Depends(_svc),
    current_user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> BudgetOut:
    budget = svc.get_budget(budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    enforce_ministry_access(current_user, budget.ministry)
    return BudgetOut.model_validate(budget)


@router.get("/{budget_id}/transactions")
def list_transactions(
    budget_id: int,
    svc: BudgetService = Depends(_svc),
    current_user: dict = Depends(require_permission(Permission.BUDGET_READ)),
) -> dict:
    budget = svc.get_budget(budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    enforce_ministry_access(current_user, budget.ministry)
    transactions = svc.list_transactions(budget_id)
    return {
        "count": len(transactions),
        "transactions": [TransactionOut.model_validate(item).model_dump() for item in transactions],
    }


@router.post("/{budget_id}/transactions", response_model=TransactionOut, status_code=201)
def create_transaction(
    budget_id: int,
    body: TransactionCreate,
    db: Session = Depends(get_db),
    svc: BudgetService = Depends(_svc),
    current_user: dict = Depends(require_permission(Permission.BUDGET_WRITE)),
) -> TransactionOut:
    if body.budget_id != budget_id:
        raise HTTPException(status_code=400, detail="budget_id in body must match URL")
    budget = svc.get_budget(budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    enforce_ministry_access(current_user, budget.ministry)
    transaction = svc.create_transaction(
        body.budget_id,
        body.amount,
        body.description,
        body.transaction_type,
        body.reference_number,
        body.beneficiary,
        commit=False,
    )
    record_audit_event(
        db,
        current_user,
        "budget.transaction_created",
        "transaction",
        transaction.id,
        ministry=budget.ministry,
        detail={"budget_id": budget.id, "reference_number": transaction.reference_number},
    )
    return TransactionOut.model_validate(transaction)
