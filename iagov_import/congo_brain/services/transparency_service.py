"""TranspaFin — financial transparency and compliance service."""

from sqlalchemy.orm import Session

from congo_brain.models.transparency import TransparencyReport


class TransparencyService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_reports(self, ministry: str | None = None, status: str | None = None) -> list[TransparencyReport]:
        q = self.db.query(TransparencyReport)
        if ministry:
            q = q.filter(TransparencyReport.ministry.ilike(f"%{ministry}%"))
        if status:
            q = q.filter(TransparencyReport.status == status)
        return q.all()

    def get_report(self, report_id: int) -> TransparencyReport | None:
        return self.db.query(TransparencyReport).filter(TransparencyReport.id == report_id).first()

    def create_report(self, **kwargs) -> TransparencyReport:  # type: ignore[no-untyped-def]
        report = TransparencyReport(**kwargs)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_dashboard(self) -> dict:
        reports = self.db.query(TransparencyReport).all()
        if not reports:
            return {
                "total_reports": 0,
                "avg_transparency_score": 0.0,
                "avg_compliance_rate": 0.0,
                "by_ministry": [],
                "by_status": {},
            }

        by_ministry: dict[str, dict] = {}
        by_status: dict[str, int] = {}
        for r in reports:
            by_status[r.status] = by_status.get(r.status, 0) + 1
            if r.ministry not in by_ministry:
                by_ministry[r.ministry] = {"ministry": r.ministry, "scores": [], "compliance": []}
            by_ministry[r.ministry]["scores"].append(r.transparency_score)
            by_ministry[r.ministry]["compliance"].append(r.compliance_rate)

        ministry_summary = []
        for m, data in by_ministry.items():
            ministry_summary.append({
                "ministry": m,
                "avg_transparency_score": round(sum(data["scores"]) / len(data["scores"]), 1),
                "avg_compliance_rate": round(sum(data["compliance"]) / len(data["compliance"]), 1),
                "report_count": len(data["scores"]),
            })

        total_scores = [r.transparency_score for r in reports]
        total_compliance = [r.compliance_rate for r in reports]

        return {
            "total_reports": len(reports),
            "avg_transparency_score": round(sum(total_scores) / len(total_scores), 1),
            "avg_compliance_rate": round(sum(total_compliance) / len(total_compliance), 1),
            "by_ministry": ministry_summary,
            "by_status": by_status,
        }
