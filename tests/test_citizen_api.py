"""Tests for public citizen services endpoints (no auth required)."""

from fastapi.testclient import TestClient


class TestCitizenEndpoints:
    def test_get_procedures(self, client: TestClient) -> None:
        response = client.get("/api/v1/procedures")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "procedures" in data

    def test_get_contacts(self, client: TestClient) -> None:
        response = client.get("/api/v1/contacts")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "contacts" in data

    def test_get_rights(self, client: TestClient) -> None:
        response = client.get("/api/v1/rights")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "rights" in data

    def test_get_faq(self, client: TestClient) -> None:
        response = client.get("/api/v1/faq")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "faq" in data

    def test_get_categories(self, client: TestClient) -> None:
        response = client.get("/api/v1/categories")
        assert response.status_code == 200

    def test_search_procedures(self, client: TestClient) -> None:
        response = client.get("/api/v1/procedures/search/?q=passeport")
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert data["query"] == "passeport"

    def test_health_check(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200

    def test_root_serves_index(self, client: TestClient) -> None:
        response = client.get("/")
        assert response.status_code == 200
