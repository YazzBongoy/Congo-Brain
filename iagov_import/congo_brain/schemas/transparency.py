"""Transparency report schemas."""

from datetime import datetime

from pydantic import BaseModel


class TransparencyReportCreate(BaseModel):
    ministry: str
    period: str
    transparency_score: float
    compliance_rate: float
    audit_findings: str | None = None
    recommendations: str | None = None
    status: str = "draft"


class TransparencyReportOut(BaseModel):
    id: int
    ministry: str
    period: str
    transparency_score: float
    compliance_rate: float
    audit_findings: str | None
    recommendations: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TransparencyDashboard(BaseModel):
    total_reports: int
    avg_transparency_score: float
    avg_compliance_rate: float
    by_ministry: list[dict]
    by_status: dict[str, int]
