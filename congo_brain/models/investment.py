"""Investment model for InvestSmart module."""

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from congo_brain.core.database import Base


class Investment(Base):
    __tablename__ = "investments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_name: Mapped[str] = mapped_column(String(300), nullable=False)
    sector: Mapped[str] = mapped_column(String(100), nullable=False)
    province: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    total_budget: Mapped[float] = mapped_column(Float, nullable=False)
    spent_amount: Mapped[float] = mapped_column(Float, default=0.0)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="planned")
    roi_score: Mapped[float] = mapped_column(Float, default=0.0)
    efficiency_score: Mapped[float] = mapped_column(Float, default=0.0)
    social_impact_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def budget_execution(self) -> float:
        if self.total_budget == 0:
            return 0.0
        return round(self.spent_amount / self.total_budget * 100, 1)
