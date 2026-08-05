"""Risk analysis for PeaceNet — aggregates security alerts by province."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from congo_brain.models.security_alert import SecurityAlert


SEVERITY_WEIGHT = {"critical": 4, "high": 3, "medium": 2, "low": 1}


def analyze_risk_by_province(alerts: list["SecurityAlert"]) -> list[dict]:
    """Aggregate alerts per province and compute a weighted risk index.

    Returns a sorted list (highest risk first) of province summaries.
    """
    provinces: dict[str, dict] = {}
    for a in alerts:
        if a.province not in provinces:
            provinces[a.province] = {"province": a.province, "total_alerts": 0, "active": 0, "weighted_score": 0.0}
        provinces[a.province]["total_alerts"] += 1
        if not a.is_resolved:
            provinces[a.province]["active"] += 1
        w = SEVERITY_WEIGHT.get(a.severity.lower(), 1)
        provinces[a.province]["weighted_score"] += a.risk_score * w

    result = list(provinces.values())
    for p in result:
        cnt = p["total_alerts"]
        p["risk_index"] = round(p["weighted_score"] / cnt, 1) if cnt else 0.0
    result.sort(key=lambda x: x["risk_index"], reverse=True)
    return result
