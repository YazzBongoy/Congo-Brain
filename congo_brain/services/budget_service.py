"""BudgetGuard — budget monitoring and anomaly detection service."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from congo_brain.models.budget import Budget, Transaction
from congo_brain.services.ai.anomaly_detector import detect_anomalies


class BudgetService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_budgets(self, ministry: str | None = None, fiscal_year: int | None = None) -> list[Budget]:
        q = self.db.query(Budget)
        if ministry:
            q = q.filter(Budget.ministry.ilike(f"%{ministry}%"))
        if fiscal_year:
            q = q.filter(Budget.fiscal_year == fiscal_year)
        return q.all()

    def get_budget(self, budget_id: int) -> Budget | None:
        return self.db.query(Budget).filter(Budget.id == budget_id).first()

    def create_budget(
        self, ministry: str, sector: str, allocated_amount: float,
        fiscal_year: int, spent_amount: float = 0.0,
    ) -> Budget:
        b = Budget(
            ministry=ministry, sector=sector,
            allocated_amount=allocated_amount,
            spent_amount=spent_amount, fiscal_year=fiscal_year,
        )
        self.db.add(b)
        self.db.commit()
        self.db.refresh(b)
        return b

    def get_status(self) -> dict:
        budgets = self.db.query(Budget).all()
        total_alloc = sum(b.allocated_amount for b in budgets)
        total_spent = sum(b.spent_amount for b in budgets)
        by_ministry: dict[str, dict] = {}
        for b in budgets:
            if b.ministry not in by_ministry:
                by_ministry[b.ministry] = {"ministry": b.ministry, "allocated": 0.0, "spent": 0.0}
            by_ministry[b.ministry]["allocated"] += b.allocated_amount
            by_ministry[b.ministry]["spent"] += b.spent_amount
        for v in by_ministry.values():
            v["execution_rate"] = round(v["spent"] / v["allocated"] * 100, 1) if v["allocated"] else 0.0
        return {
            "total_budgets": len(budgets),
            "total_allocated": total_alloc,
            "total_spent": total_spent,
            "overall_execution_rate": round(total_spent / total_alloc * 100, 1) if total_alloc else 0.0,
            "by_ministry": list(by_ministry.values()),
        }

    # -- Transactions --

    def list_transactions(self, budget_id: int | None = None) -> list[Transaction]:
        q = self.db.query(Transaction)
        if budget_id:
            q = q.filter(Transaction.budget_id == budget_id)
        return q.all()

    def create_transaction(
        self, budget_id: int, amount: float, description: str,
        transaction_type: str, reference_number: str,
        beneficiary: str | None = None,
    ) -> Transaction:
        t = Transaction(
            budget_id=budget_id,
            amount=amount,
            description=description,
            transaction_type=transaction_type,
            beneficiary=beneficiary,
            reference_number=reference_number,
        )
        self.db.add(t)
        self.db.commit()
        self.db.refresh(t)

        budget = self.db.query(Budget).filter(Budget.id == budget_id).first()
        if budget:
            budget.spent_amount += amount
            self.db.commit()
        return t

    def run_anomaly_detection(self) -> dict:
        transactions = self.db.query(Transaction).all()
        if not transactions:
            return {
                "total_transactions": 0, "anomalies_detected": 0,
                "anomaly_rate": 0.0, "anomalies": [], "rules_applied": [],
            }

        budgets = self.db.query(Budget).all()
        anomalies = detect_anomalies(transactions, budgets=budgets)
        self.db.commit()

        rules_applied = [
            "z-score (ecart statistique global)",
            "z-score intra-budget (ecart au sein du meme budget)",
            "mots-cles suspects (description)",
            "montants ronds (zeros consecutifs)",
            "doublons (montants quasi-identiques)",
            "depassement budgetaire (depense > allocation)",
            "ratio budget (transaction > 40% du budget)",
        ]

        return {
            "total_transactions": len(transactions),
            "anomalies_detected": len(anomalies),
            "anomaly_rate": round(len(anomalies) / len(transactions) * 100, 1),
            "rules_applied": rules_applied,
            "anomalies": anomalies,
        }

    def get_ministry_summary(self) -> list[dict]:
        rows = (
            self.db.query(
                Budget.ministry,
                func.sum(Budget.allocated_amount).label("allocated"),
                func.sum(Budget.spent_amount).label("spent"),
                func.count(Budget.id).label("count"),
            )
            .group_by(Budget.ministry)
            .all()
        )
        result = []
        for r in rows:
            alloc = float(r.allocated or 0)
            spent = float(r.spent or 0)
            result.append({
                "ministry": r.ministry,
                "allocated": alloc,
                "spent": spent,
                "count": r.count,
                "execution_rate": round(spent / alloc * 100, 1) if alloc else 0.0,
            })
        return result
