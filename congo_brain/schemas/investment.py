"""Investment schemas."""

from datetime import date, datetime

from pydantic import BaseModel


class InvestmentCreate(BaseModel):
    project_name: str
    sector: str
    province: str
    description: str | None = None
    total_budget: float
    spent_amount: float = 0.0
    start_date: date
    expected_end_date: date
    status: str = "planned"
    roi_score: float = 0.0
    efficiency_score: float = 0.0
    social_impact_score: float = 0.0


class InvestmentOut(BaseModel):
    id: int
    project_name: str
    sector: str
    province: str
    description: str | None
    total_budget: float
    spent_amount: float
    start_date: date
    expected_end_date: date
    status: str
    roi_score: float
    efficiency_score: float
    social_impact_score: float
    budget_execution: float
    created_at: datetime

    model_config = {"from_attributes": True}


class PortfolioOptimization(BaseModel):
    budget_limit: float
    selected_projects: list[InvestmentOut]
    total_cost: float
    expected_total_roi: float
    projects_excluded: list[InvestmentOut]
