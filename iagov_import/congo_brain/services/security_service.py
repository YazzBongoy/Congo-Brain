"""PeaceNet — security monitoring and social cohesion service."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from congo_brain.models.security_alert import SecurityAlert
from congo_brain.services.ai.risk_analyzer import analyze_risk_by_province


class SecurityService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_alerts(
        self, province: str | None = None,
        severity: str | None = None, active_only: bool = False,
    ) -> list[SecurityAlert]:
        q = self.db.query(SecurityAlert)
        if province:
            q = q.filter(SecurityAlert.province.ilike(f"%{province}%"))
        if severity:
            q = q.filter(SecurityAlert.severity == severity)
        if active_only:
            q = q.filter(SecurityAlert.is_resolved.is_(False))
        return q.order_by(SecurityAlert.risk_score.desc()).all()

    def get_alert(self, alert_id: int) -> SecurityAlert | None:
        return self.db.query(SecurityAlert).filter(SecurityAlert.id == alert_id).first()

    def create_alert(self, **kwargs) -> SecurityAlert:  # type: ignore[no-untyped-def]
        alert = SecurityAlert(**kwargs)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def resolve_alert(self, alert_id: int) -> SecurityAlert | None:
        alert = self.db.query(SecurityAlert).filter(SecurityAlert.id == alert_id).first()
        if alert:
            alert.is_resolved = True
            alert.resolved_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(alert)
        return alert

    def get_dashboard(self) -> dict:
        alerts = self.db.query(SecurityAlert).all()
        if not alerts:
            return {
                "total_alerts": 0,
                "active_alerts": 0,
                "resolved_alerts": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "avg_risk_score": 0.0,
                "by_province": [],
            }

        active = [a for a in alerts if not a.is_resolved]
        resolved = [a for a in alerts if a.is_resolved]
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for a in alerts:
            sev = a.severity.lower()
            if sev in severity_counts:
                severity_counts[sev] += 1

        by_province = analyze_risk_by_province(alerts)

        return {
            "total_alerts": len(alerts),
            "active_alerts": len(active),
            "resolved_alerts": len(resolved),
            "critical_count": severity_counts["critical"],
            "high_count": severity_counts["high"],
            "medium_count": severity_counts["medium"],
            "low_count": severity_counts["low"],
            "avg_risk_score": round(sum(a.risk_score for a in alerts) / len(alerts), 1),
            "by_province": by_province,
        }
