"""TransparencyReport model for TranspaFin module."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from congo_brain.core.database import Base


class TransparencyReport(Base):
    __tablename__ = "transparency_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ministry: Mapped[str] = mapped_column(String(200), nullable=False)
    period: Mapped[str] = mapped_column(String(50), nullable=False)
    transparency_score: Mapped[float] = mapped_column(Float, nullable=False)
    compliance_rate: Mapped[float] = mapped_column(Float, nullable=False)
    audit_findings: Mapped[str] = mapped_column(Text, nullable=True)
    recommendations: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
