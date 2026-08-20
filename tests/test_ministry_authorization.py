"""Authorization tests for ministry-scoped budget access."""

from fastapi.testclient import TestClient


def _create_officer_headers(client: TestClient, auth_headers: dict, ministry: str) -> dict:
    created = client.post(
        "/api/v1/auth/users",
        headers=auth_headers,
        json={
            "username": "health-budget-officer",
            "email": "health-budget-officer@example.cd",
            "password": "strong-pass",
            "role": "ministry_budget_officer",
            "ministry": ministry,
        },
    )
    assert created.status_code == 201
    login = client.post(
        "/api/v1/auth/login",
        json={"username": "health-budget-officer", "password": "strong-pass"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _create_budget(client: TestClient, headers: dict, ministry: str, sector: str) -> dict:
    response = client.post(
        "/api/v1/budgets",
        headers=headers,
        json={
            "ministry": ministry,
            "sector": sector,
            "allocated_amount": 1000,
            "spent_amount": 100,
            "fiscal_year": 2026,
        },
    )
    assert response.status_code == 201
    return response.json()


class TestMinistryBudgetIsolation:
    def test_officer_lists_only_assigned_ministry(self, client: TestClient, auth_headers: dict) -> None:
        _create_budget(client, auth_headers, "Santé Publique", "Santé")
        _create_budget(client, auth_headers, "Finances", "Administration")
        officer_headers = _create_officer_headers(client, auth_headers, "Santé Publique")

        response = client.get("/api/v1/budgets", headers=officer_headers)

        assert response.status_code == 200
        assert response.json()["count"] == 1
        assert {item["ministry"] for item in response.json()["budgets"]} == {"Santé Publique"}

    def test_officer_cannot_override_ministry_filter(self, client: TestClient, auth_headers: dict) -> None:
        _create_budget(client, auth_headers, "Finances", "Administration")
        officer_headers = _create_officer_headers(client, auth_headers, "Santé Publique")

        response = client.get("/api/v1/budgets?ministry=Finances", headers=officer_headers)

        assert response.status_code == 403

    def test_officer_cannot_read_other_ministry_budget(self, client: TestClient, auth_headers: dict) -> None:
        finance_budget = _create_budget(client, auth_headers, "Finances", "Administration")
        officer_headers = _create_officer_headers(client, auth_headers, "Santé Publique")

        response = client.get(f"/api/v1/budgets/{finance_budget['id']}", headers=officer_headers)

        assert response.status_code == 403

    def test_officer_cannot_create_budget_for_other_ministry(self, client: TestClient, auth_headers: dict) -> None:
        officer_headers = _create_officer_headers(client, auth_headers, "Santé Publique")

        response = client.post(
            "/api/v1/budgets",
            headers=officer_headers,
            json={
                "ministry": "Finances",
                "sector": "Administration",
                "allocated_amount": 1000,
                "spent_amount": 0,
                "fiscal_year": 2026,
            },
        )

        assert response.status_code == 403

    def test_officer_can_create_budget_for_assigned_ministry(self, client: TestClient, auth_headers: dict) -> None:
        officer_headers = _create_officer_headers(client, auth_headers, "Santé Publique")

        response = client.post(
            "/api/v1/budgets",
            headers=officer_headers,
            json={
                "ministry": "Santé Publique",
                "sector": "Santé",
                "allocated_amount": 1000,
                "spent_amount": 0,
                "fiscal_year": 2026,
            },
        )

        assert response.status_code == 201


class TestMinistryTransparencyIsolation:
    def test_officer_lists_only_assigned_ministry_reports(self, client: TestClient, auth_headers: dict) -> None:
        for ministry in ["Santé Publique", "Finances"]:
            response = client.post(
                "/api/v1/transparency",
                headers=auth_headers,
                json={
                    "ministry": ministry,
                    "period": "2026-Q1",
                    "transparency_score": 80,
                    "compliance_rate": 75,
                },
            )
            assert response.status_code == 201
        officer_headers = _create_officer_headers(client, auth_headers, "Santé Publique")

        response = client.get("/api/v1/transparency", headers=officer_headers)

        assert response.status_code == 200
        assert response.json()["count"] == 1
        assert response.json()["reports"][0]["ministry"] == "Santé Publique"

    def test_officer_cannot_create_other_ministry_report(self, client: TestClient, auth_headers: dict) -> None:
        officer_headers = _create_officer_headers(client, auth_headers, "Santé Publique")

        response = client.post(
            "/api/v1/transparency",
            headers=officer_headers,
            json={
                "ministry": "Finances",
                "period": "2026-Q1",
                "transparency_score": 80,
                "compliance_rate": 75,
            },
        )

        assert response.status_code == 403


class TestNationalAnalyticsIsolation:
    def test_ministry_officer_cannot_access_national_analytics(
        self,
        client: TestClient,
        auth_headers: dict,
    ) -> None:
        officer_headers = _create_officer_headers(client, auth_headers, "Santé Publique")

        responses = [
            client.get("/api/v1/geos/dashboard", headers=officer_headers),
            client.get("/api/v1/economic/dashboard", headers=officer_headers),
            client.get("/api/v1/ia-gov/dashboard", headers=officer_headers),
            client.post("/graphql", headers=officer_headers, json={"query": "{ ministries { name } }"}),
        ]

        assert [response.status_code for response in responses] == [403, 403, 403, 403]

    def test_public_viewer_cannot_access_national_analytics(
        self,
        client: TestClient,
        viewer_headers: dict,
    ) -> None:
        responses = [
            client.get("/api/v1/geos/dashboard", headers=viewer_headers),
            client.get("/api/v1/economic/dashboard", headers=viewer_headers),
            client.get("/api/v1/ia-gov/dashboard", headers=viewer_headers),
            client.post("/graphql", headers=viewer_headers, json={"query": "{ ministries { name } }"}),
        ]

        assert [response.status_code for response in responses] == [403, 403, 403, 403]
