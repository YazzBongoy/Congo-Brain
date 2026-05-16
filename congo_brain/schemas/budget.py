"""Budget and Transaction schemas."""

from datetime import datetime

from pydantic import BaseModel


class BudgetCreate(BaseModel):
    ministry: str
    sector: str
    allocated_amount: float
    spent_amount: float = 0.0
    fiscal_year: int


class BudgetOut(BaseModel):
    id: int
    ministry: str
    sector: str
    allocated_amount: float
    spent_amount: float
    fiscal_year: int
    execution_rate: float
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionCreate(BaseModel):
    budget_id: int
    amount: float
    description: str
    transaction_type: str
    beneficiary: str | None = None
    reference_number: str


class TransactionOut(BaseModel):
    id: int
    budget_id: int
    amount: float
    description: str
    transaction_type: str
    beneficiary: str | None
    reference_number: str
    is_anomaly: bool
    anomaly_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class BudgetStatusOut(BaseModel):
    total_budgets: int
    total_allocated: float
    total_spent: float
    overall_execution_rate: float
    by_ministry: list[dict]


class AnomalyReport(BaseModel):
    total_transactions: int
    anomalies_detected: int
    anomaly_rate: float
    anomalies: list[TransactionOut]
