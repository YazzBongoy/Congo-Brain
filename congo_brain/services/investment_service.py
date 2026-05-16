"""InvestSmart — investment analysis and portfolio optimization service."""

from sqlalchemy.orm import Session

from congo_brain.models.investment import Investment
from congo_brain.services.ai.investment_optimizer import optimize_portfolio


class InvestmentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_investments(
        self, status: str | None = None,
        province: str | None = None, sector: str | None = None,
    ) -> list[Investment]:
        q = self.db.query(Investment)
        if status:
            q = q.filter(Investment.status == status)
        if province:
            q = q.filter(Investment.province.ilike(f"%{province}%"))
        if sector:
            q = q.filter(Investment.sector.ilike(f"%{sector}%"))
        return q.all()

    def get_investment(self, inv_id: int) -> Investment | None:
        return self.db.query(Investment).filter(Investment.id == inv_id).first()

    def create_investment(self, **kwargs) -> Investment:  # type: ignore[no-untyped-def]
        inv = Investment(**kwargs)
        self.db.add(inv)
        self.db.commit()
        self.db.refresh(inv)
        return inv

    def optimize(self, budget_limit: float) -> dict:
        investments = self.db.query(Investment).filter(Investment.status.in_(["planned", "in_progress"])).all()
        return optimize_portfolio(investments, budget_limit)

    def get_summary(self) -> dict:
        investments = self.db.query(Investment).all()
        if not investments:
            return {
                "total_projects": 0,
                "total_budget": 0.0,
                "total_spent": 0.0,
                "avg_roi": 0.0,
                "by_status": {},
                "by_sector": {},
                "by_province": {},
            }

        by_status: dict[str, int] = {}
        by_sector: dict[str, list[dict]] = {}
        by_province: dict[str, int] = {}
        total_roi = 0.0
        total_budget = 0.0
        total_spent = 0.0

        for inv in investments:
            by_status[inv.status] = by_status.get(inv.status, 0) + 1
            by_province[inv.province] = by_province.get(inv.province, 0) + 1
            if inv.sector not in by_sector:
                by_sector[inv.sector] = []
            by_sector[inv.sector].append({"project": inv.project_name, "roi": inv.roi_score})
            total_roi += inv.roi_score
            total_budget += inv.total_budget
            total_spent += inv.spent_amount

        return {
            "total_projects": len(investments),
            "total_budget": total_budget,
            "total_spent": total_spent,
            "avg_roi": round(total_roi / len(investments), 1),
            "by_status": by_status,
            "by_sector": {k: len(v) for k, v in by_sector.items()},
            "by_province": by_province,
        }
