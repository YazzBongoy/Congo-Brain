"""Risk analysis for PeaceNet — aggregates security alerts by province.

Enhanced with trend tracking, province comparison, and escalation rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from congo_brain.models.security_alert import SecurityAlert


SEVERITY_WEIGHT = {"critical": 4, "high": 3, "medium": 2, "low": 1}

# Escalation thresholds
ESCALATION_THRESHOLDS = {
    "critical": 5,   # 5+ critical alerts -> escalated
    "high": 10,      # 10+ high alerts -> escalated
    "medium": 20,    # 20+ medium alerts -> escalated
}


@dataclass
class ProvinceRisk:
    """Detailed risk profile for a province."""
    province: str
    total_alerts: int = 0
    active_alerts: int = 0
    resolved_alerts: int = 0
    risk_index: float = 0.0
    severity_breakdown: dict[str, int] = field(default_factory=dict)
    is_escalated: bool = False
    escalation_reasons: list[str] = field(default_factory=list)
    latest_alert_date: str | None = None


@dataclass
class RiskTrend:
    """Risk trend data point for time-series analysis."""
    period: str
    total_alerts: int
    risk_index: float
    severity_breakdown: dict[str, int]


def analyze_risk_by_province(alerts: list["SecurityAlert"]) -> list[dict]:
    """Aggregate alerts per province and compute a weighted risk index.

    Returns a sorted list (highest risk first) of province summaries.
    """
    provinces: dict[str, ProvinceRisk] = {}

    for a in alerts:
        if a.province not in provinces:
            provinces[a.province] = ProvinceRisk(province=a.province)
        p = provinces[a.province]
        p.total_alerts += 1
        if not a.is_resolved:
            p.active_alerts += 1
        else:
            p.resolved_alerts += 1

        sev = a.severity.lower()
        p.severity_breakdown[sev] = p.severity_breakdown.get(sev, 0) + 1

        w = SEVERITY_WEIGHT.get(sev, 1)
        p.risk_index += a.risk_score * w

        # Track latest alert
        alert_date = a.created_at.isoformat() if a.created_at else None
        if alert_date and (p.latest_alert_date is None or alert_date > p.latest_alert_date):
            p.latest_alert_date = alert_date

    # Finalize risk index and check escalation
    result = []
    for p in provinces.values():
        if p.total_alerts > 0:
            p.risk_index = round(p.risk_index / p.total_alerts, 1)

        # Check escalation rules
        for severity, threshold in ESCALATION_THRESHOLDS.items():
            count = p.severity_breakdown.get(severity, 0)
            if count >= threshold:
                p.is_escalated = True
                p.escalation_reasons.append(
                    f"{count} alertes {severity} (seuil: {threshold})"
                )

        result.append({
            "province": p.province,
            "total_alerts": p.total_alerts,
            "active_alerts": p.active_alerts,
            "resolved_alerts": p.resolved_alerts,
            "risk_index": p.risk_index,
            "severity_breakdown": p.severity_breakdown,
            "is_escalated": p.is_escalated,
            "escalation_reasons": p.escalation_reasons,
            "latest_alert_date": p.latest_alert_date,
        })

    result.sort(key=lambda x: x["risk_index"], reverse=True)
    return result


def compute_risk_trends(alerts: list["SecurityAlert"], group_by: str = "month") -> list[dict]:
    """Compute risk trends over time.

    Args:
        alerts: list of SecurityAlert ORM objects.
        group_by: time grouping - "month" or "week".

    Returns:
        list of time-period risk summaries sorted chronologically.
    """
    if not alerts:
        return []

    periods: dict[str, list["SecurityAlert"]] = {}

    for a in alerts:
        if not a.created_at:
            continue
        if group_by == "week":
            key = a.created_at.strftime("%Y-W%W")
        else:
            key = a.created_at.strftime("%Y-%m")
        periods.setdefault(key, []).append(a)

    trends = []
    for period, period_alerts in sorted(periods.items()):
        total = len(period_alerts)
        weighted_sum = sum(
            a.risk_score * SEVERITY_WEIGHT.get(a.severity.lower(), 1)
            for a in period_alerts
        )
        risk_index = round(weighted_sum / total, 1) if total else 0.0

        severity_breakdown: dict[str, int] = {}
        for a in period_alerts:
            sev = a.severity.lower()
            severity_breakdown[sev] = severity_breakdown.get(sev, 0) + 1

        trends.append({
            "period": period,
            "total_alerts": total,
            "risk_index": risk_index,
            "severity_breakdown": severity_breakdown,
        })

    return trends


def compare_provinces(province_risks: list[dict], top_n: int = 5) -> dict:
    """Generate a comparison summary of the top N highest-risk provinces.

    Args:
        province_risks: output from analyze_risk_by_province.
        top_n: number of top provinces to compare.

    Returns:
        dict with comparison data.
    """
    top = province_risks[:top_n]
    if not top:
        return {"top_provinces": [], "avg_risk_index": 0.0, "most_active": None}

    avg_risk = round(sum(p["risk_index"] for p in top) / len(top), 1)
    most_active = max(top, key=lambda p: p["total_alerts"])

    return {
        "top_provinces": [
            {
                "province": p["province"],
                "risk_index": p["risk_index"],
                "active_alerts": p["active_alerts"],
                "is_escalated": p["is_escalated"],
            }
            for p in top
        ],
        "avg_risk_index": avg_risk,
        "most_active": most_active["province"],
    }
