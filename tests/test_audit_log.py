"""Tests for append-only privileged-operation audit logging."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import Session

from congo_brain.models.audit import AuditEvent
from congo_brain.models.budget import Budget, Transaction
from congo_brain.models.investment import Investment
from congo_brain.models.security_alert import SecurityAlert
from congo_brain.models.transparency import TransparencyReport
from congo_brain.models.user import User
from congo_brain.services.audit_service import record_audit_event


class TestAuditLog:
    @staticmethod
    def _fail_audit(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("audit write failed")

    def test_admin_user_creation_is_audited(self, client: TestClient, auth_headers: dict) -> None:
        created = client.post(
            "/api/v1/auth/users",
            headers=auth_headers,
            json={
                "username": "audited-user",
                "email": "audited-user@example.cd",
                "password": "strong-pass",
                "role": "auditor",
            },
        )
        assert created.status_code == 201

        response = client.get("/api/v1/auth/audit-log", headers=auth_headers)

        assert response.status_code == 200
        event = response.json()["events"][0]
        assert event["actor_subject"] == "testadmin"
        assert event["action"] == "user.created"
        assert event["resource_type"] == "user"
        assert event["resource_id"] == str(created.json()["id"])
        assert len(event["event_hash"]) == 64

    def test_viewer_cannot_read_audit_log(self, client: TestClient, viewer_headers: dict) -> None:
        response = client.get("/api/v1/auth/audit-log", headers=viewer_headers)
        assert response.status_code == 403

    def test_privileged_budget_write_is_audited(self, client: TestClient, auth_headers: dict) -> None:
        response = client.post(
            "/api/v1/budgets",
            headers=auth_headers,
            json={
                "ministry": "Finances",
                "sector": "Administration",
                "allocated_amount": 1000,
                "spent_amount": 0,
                "fiscal_year": 2026,
            },
        )
        assert response.status_code == 201

        audit_response = client.get("/api/v1/auth/audit-log", headers=auth_headers)
        actions = [event["action"] for event in audit_response.json()["events"]]
        assert "budget.created" in actions

    def test_optimization_is_audited(self, client: TestClient, auth_headers: dict) -> None:
        response = client.post(
            "/api/v1/geos/optimize",
            headers=auth_headers,
            json={"budget": 1000},
        )
        assert response.status_code == 200

        audit_response = client.get("/api/v1/auth/audit-log", headers=auth_headers)
        actions = [event["action"] for event in audit_response.json()["events"]]
        assert "optimization.executed" in actions

    def test_privileged_domain_writes_are_audited(self, client: TestClient, auth_headers: dict) -> None:
        transparency = client.post(
            "/api/v1/transparency",
            headers=auth_headers,
            json={
                "ministry": "Finances",
                "period": "2026-Q1",
                "transparency_score": 80,
                "compliance_rate": 75,
            },
        )
        assert transparency.status_code == 201
        investment = client.post(
            "/api/v1/investments",
            headers=auth_headers,
            json={
                "project_name": "Projet audité",
                "sector": "Infrastructure",
                "province": "Kinshasa",
                "total_budget": 1000,
                "start_date": "2026-01-01",
                "expected_end_date": "2027-01-01",
            },
        )
        assert investment.status_code == 201
        alert = client.post(
            "/api/v1/security/alerts",
            headers=auth_headers,
            json={
                "alert_type": "operational",
                "severity": "high",
                "province": "Kinshasa",
                "description": "Audit test",
                "risk_score": 80,
            },
        )
        assert alert.status_code == 201
        resolved = client.post(
            f"/api/v1/security/alerts/{alert.json()['id']}/resolve",
            headers=auth_headers,
        )
        assert resolved.status_code == 200

        audit_response = client.get("/api/v1/auth/audit-log", headers=auth_headers)
        actions = {event["action"] for event in audit_response.json()["events"]}
        assert {
            "transparency_report.created",
            "investment.created",
            "security_alert.created",
            "security_alert.resolved",
        }.issubset(actions)

    def test_simulation_and_analysis_routes_are_audited(self, client: TestClient, auth_headers: dict) -> None:
        requests = [
            client.post(
                "/api/v1/ia-gov/optimizer/simulate",
                headers=auth_headers,
                json={"policy_name": "Audit policy", "sector_changes": {}},
            ),
            client.post("/api/v1/ia-gov/producer-surplus/simulate-reform", headers=auth_headers),
            client.post(
                "/api/v1/ia-gov/twin/simulate",
                headers=auth_headers,
                json={"province": "Kinshasa", "sector": "infrastructure", "amount": 100},
            ),
            client.post(
                "/api/v1/ia-gov/decision",
                headers=auth_headers,
                json={"question": "Comment prioriser les investissements ?", "budget": 1000},
            ),
            client.post(
                "/api/v1/economic/welfare/sectors",
                headers=auth_headers,
                json={"sector": "Test", "cs": 1, "ps": 2, "revenue": 3},
            ),
            client.post("/api/v1/economic/investments/optimize?budget=1000", headers=auth_headers),
            client.post("/api/v1/economic/investments/scenarios", headers=auth_headers),
            client.post(
                "/api/v1/economic/nwi/compute",
                headers=auth_headers,
                json={
                    "consumer_surplus": 1,
                    "producer_surplus": 2,
                    "government_revenue": 3,
                    "sustainability": 4,
                },
            ),
            client.get("/api/v1/economic/corruption/scenarios", headers=auth_headers),
            client.get("/api/v1/investments/optimize?budget=1000", headers=auth_headers),
            client.get("/api/v1/investments/scenarios?budgets=1000,2000", headers=auth_headers),
            client.get("/api/v1/geos/dashboard", headers=auth_headers),
            client.get("/api/v1/geos/predictions/compare?years=2", headers=auth_headers),
            client.get("/api/v1/geos/predictions/baseline?years=2", headers=auth_headers),
            client.get("/api/v1/geos/reports/snn.pdf?scenario=baseline&years=2", headers=auth_headers),
            client.get("/api/v1/economic/dashboard", headers=auth_headers),
        ]
        assert [response.status_code for response in requests] == [200] * len(requests)

        audit_response = client.get("/api/v1/auth/audit-log", headers=auth_headers)
        assert audit_response.json()["chain_valid"] is True
        actions = {event["action"] for event in audit_response.json()["events"]}
        assert {
            "policy_simulation.executed",
            "producer_reform_simulation.executed",
            "digital_twin_simulation.executed",
            "decision_analysis.executed",
            "welfare_sector_analysis.executed",
            "economic_investment_optimization.executed",
            "economic_investment_scenarios.executed",
            "national_welfare_analysis.executed",
            "corruption_scenario.executed",
            "investment_portfolio_optimization.executed",
            "investment_portfolio_scenarios.executed",
            "geos_dashboard.computed",
            "geos_scenarios.compared",
            "geos_prediction.executed",
            "geos_report.exported",
            "economic_dashboard.computed",
        }.issubset(actions)

    def test_audit_events_are_immutable(self, db_session: Session) -> None:
        event = AuditEvent(
            actor_subject="admin",
            actor_username="admin",
            actor_role="admin",
            action="test.created",
            resource_type="test",
            resource_id="1",
            ministry=None,
            detail="{}",
            previous_hash="0" * 64,
            event_hash="1" * 64,
        )
        db_session.add(event)
        db_session.commit()

        event.action = "tampered"
        with pytest.raises(ValueError, match="immutable"):
            db_session.commit()
        db_session.rollback()

        db_session.delete(event)
        with pytest.raises(ValueError, match="immutable"):
            db_session.commit()

    def test_sensitive_detail_fields_are_recursively_redacted(self, db_session: Session) -> None:
        event = record_audit_event(
            db_session,
            {"sub": "admin", "username": "admin", "role": "admin"},
            "policy.executed",
            "policy",
            "redaction-test",
            detail={
                "safe": "visible",
                "password": "never-store-me",
                "nested": {
                    "authorization": "Bearer secret-token",
                    "client_secret": "also-secret",
                    "items": [{"api_key": "private-key"}],
                },
            },
        )

        assert "visible" in event.detail
        assert "never-store-me" not in event.detail
        assert "secret-token" not in event.detail
        assert "also-secret" not in event.detail
        assert "private-key" not in event.detail
        assert event.detail.count("[REDACTED]") == 4

    def test_user_creation_rolls_back_when_audit_fails(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from congo_brain.api.v1 import auth

        monkeypatch.setattr(auth, "record_audit_event", self._fail_audit)
        with pytest.raises(RuntimeError, match="audit write failed"):
            client.post(
                "/api/v1/auth/users",
                headers=auth_headers,
                json={
                    "username": "must-rollback",
                    "email": "must-rollback@example.cd",
                    "password": "strong-pass",
                    "role": "auditor",
                },
            )
        db_session.rollback()

        assert db_session.query(User).filter(User.username == "must-rollback").first() is None

    @pytest.mark.parametrize("operation", ["update", "delete"])
    def test_user_change_rolls_back_when_audit_fails(
        self,
        operation: str,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from congo_brain.api.v1 import auth

        created = client.post(
            "/api/v1/auth/users",
            headers=auth_headers,
            json={
                "username": f"rollback-{operation}",
                "email": f"rollback-{operation}@example.cd",
                "password": "strong-pass",
                "role": "auditor",
            },
        ).json()
        monkeypatch.setattr(auth, "record_audit_event", self._fail_audit)

        with pytest.raises(RuntimeError, match="audit write failed"):
            if operation == "update":
                client.patch(
                    f"/api/v1/auth/users/{created['id']}",
                    headers=auth_headers,
                    json={"role": "executive_viewer"},
                )
            else:
                client.delete(f"/api/v1/auth/users/{created['id']}", headers=auth_headers)
        db_session.rollback()

        persisted = db_session.query(User).filter(User.id == created["id"]).one()
        assert persisted.role == "auditor"

    def test_real_audit_flush_failure_rolls_back_request_transaction(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
    ) -> None:
        def reject_audit_insert(session: Session, _flush_context: object, _instances: object) -> None:
            if any(isinstance(item, AuditEvent) for item in session.new):
                raise RuntimeError("database rejected audit insert")

        event.listen(db_session.__class__, "before_flush", reject_audit_insert)
        try:
            with pytest.raises(RuntimeError, match="database rejected audit insert"):
                client.post(
                    "/api/v1/budgets",
                    headers=auth_headers,
                    json={
                        "ministry": "Rejected Audit Ministry",
                        "sector": "Test",
                        "allocated_amount": 1000,
                        "spent_amount": 0,
                        "fiscal_year": 2026,
                    },
                )
        finally:
            event.remove(db_session.__class__, "before_flush", reject_audit_insert)

        assert db_session.in_transaction() is False
        assert db_session.query(Budget).filter(Budget.ministry == "Rejected Audit Ministry").first() is None

    def test_budget_creation_rolls_back_when_audit_fails(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from congo_brain.api.v1 import budget

        monkeypatch.setattr(budget, "record_audit_event", self._fail_audit)
        with pytest.raises(RuntimeError, match="audit write failed"):
            client.post(
                "/api/v1/budgets",
                headers=auth_headers,
                json={
                    "ministry": "Rollback Ministry",
                    "sector": "Test",
                    "allocated_amount": 1000,
                    "spent_amount": 0,
                    "fiscal_year": 2026,
                },
            )
        db_session.rollback()

        assert db_session.query(Budget).filter(Budget.ministry == "Rollback Ministry").first() is None

    def test_transaction_and_budget_total_roll_back_when_audit_fails(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from congo_brain.api.v1 import budget

        created = client.post(
            "/api/v1/budgets",
            headers=auth_headers,
            json={
                "ministry": "Transaction Rollback",
                "sector": "Test",
                "allocated_amount": 1000,
                "spent_amount": 0,
                "fiscal_year": 2026,
            },
        ).json()
        monkeypatch.setattr(budget, "record_audit_event", self._fail_audit)
        with pytest.raises(RuntimeError, match="audit write failed"):
            client.post(
                f"/api/v1/budgets/{created['id']}/transactions",
                headers=auth_headers,
                json={
                    "budget_id": created["id"],
                    "amount": 100,
                    "description": "Must roll back",
                    "transaction_type": "expense",
                    "reference_number": "ROLLBACK-TX",
                },
            )
        db_session.rollback()

        persisted_budget = db_session.query(Budget).filter(Budget.id == created["id"]).one()
        assert persisted_budget.spent_amount == 0
        assert db_session.query(Transaction).filter(Transaction.reference_number == "ROLLBACK-TX").first() is None

    @pytest.mark.parametrize(
        ("module_name", "path", "payload", "model", "field", "value"),
        [
            (
                "investment",
                "/api/v1/investments",
                {
                    "project_name": "Rollback Investment",
                    "sector": "Infrastructure",
                    "province": "Kinshasa",
                    "total_budget": 1000,
                    "start_date": "2026-01-01",
                    "expected_end_date": "2027-01-01",
                },
                Investment,
                "project_name",
                "Rollback Investment",
            ),
            (
                "transparency",
                "/api/v1/transparency",
                {
                    "ministry": "Rollback Transparency",
                    "period": "2026-Q1",
                    "transparency_score": 80,
                    "compliance_rate": 75,
                },
                TransparencyReport,
                "ministry",
                "Rollback Transparency",
            ),
            (
                "security",
                "/api/v1/security/alerts",
                {
                    "alert_type": "operational",
                    "severity": "high",
                    "province": "Rollback Province",
                    "description": "Must roll back",
                    "risk_score": 80,
                },
                SecurityAlert,
                "province",
                "Rollback Province",
            ),
        ],
    )
    def test_domain_creation_rolls_back_when_audit_fails(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        monkeypatch: pytest.MonkeyPatch,
        module_name: str,
        path: str,
        payload: dict,
        model: type,
        field: str,
        value: str,
    ) -> None:
        from congo_brain.api.v1 import investment, security, transparency

        modules = {"investment": investment, "security": security, "transparency": transparency}
        monkeypatch.setattr(modules[module_name], "record_audit_event", self._fail_audit)
        with pytest.raises(RuntimeError, match="audit write failed"):
            client.post(path, headers=auth_headers, json=payload)
        db_session.rollback()

        assert db_session.query(model).filter(getattr(model, field) == value).first() is None

    def test_security_resolution_rolls_back_when_audit_fails(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from congo_brain.api.v1 import security

        created = client.post(
            "/api/v1/security/alerts",
            headers=auth_headers,
            json={
                "alert_type": "operational",
                "severity": "high",
                "province": "Resolution Rollback",
                "description": "Must remain unresolved",
                "risk_score": 80,
            },
        ).json()
        monkeypatch.setattr(security, "record_audit_event", self._fail_audit)

        with pytest.raises(RuntimeError, match="audit write failed"):
            client.post(f"/api/v1/security/alerts/{created['id']}/resolve", headers=auth_headers)
        db_session.rollback()

        persisted = db_session.query(SecurityAlert).filter(SecurityAlert.id == created["id"]).one()
        assert persisted.is_resolved is False
        assert persisted.resolved_at is None
