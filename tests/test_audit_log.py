"""Tests for append-only privileged-operation audit logging."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from congo_brain.models.audit import AuditEvent
from congo_brain.services.audit_service import record_audit_event


class TestAuditLog:
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
