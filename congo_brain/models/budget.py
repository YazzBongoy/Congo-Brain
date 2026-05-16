"""Budget and Transaction models for BudgetGuard module."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from congo_brain.core.database import Base


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ministry: Mapped[str] = mapped_column(String(200), nullable=False)
    sector: Mapped[str] = mapped_column(String(200), nullable=False)
    allocated_amount: Mapped[float] = mapped_column(Float, nullable=False)
    spent_amount: Mapped[float] = mapped_column(Float, default=0.0)
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="budget")

    @property
    def execution_rate(self) -> float:
        if self.allocated_amount == 0:
            return 0.0
        return round(self.spent_amount / self.allocated_amount * 100, 1)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    budget_id: Mapped[int] = mapped_column(Integer, ForeignKey("budgets.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    beneficiary: Mapped[str] = mapped_column(String(200), nullable=True)
    reference_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False)
    anomaly_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    budget: Mapped["Budget"] = relationship("Budget", back_populates="transactions")
