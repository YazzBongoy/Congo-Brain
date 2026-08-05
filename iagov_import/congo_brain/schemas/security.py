"""Security alert schemas."""

from datetime import datetime

from pydantic import BaseModel


class SecurityAlertCreate(BaseModel):
    alert_type: str
    severity: str
    province: str
    territory: str | None = None
    description: str
    risk_score: float
    recommended_action: str | None = None


class SecurityAlertOut(BaseModel):
    id: int
    alert_type: str
    severity: str
    province: str
    territory: str | None
    description: str
    risk_score: float
    is_resolved: bool
    recommended_action: str | None
    created_at: datetime
    resolved_at: datetime | None

    model_config = {"from_attributes": True}


class RiskDashboard(BaseModel):
    total_alerts: int
    active_alerts: int
    resolved_alerts: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    avg_risk_score: float
    by_province: list[dict]
