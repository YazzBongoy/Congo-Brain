"""Tests for authentication API endpoints."""

from fastapi.testclient import TestClient


class TestAuthEndpoints:
    def test_register_user(self, client: TestClient) -> None:
        response = client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "secret123",
            "role": "viewer",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["role"] == "viewer"
        assert "id" in data

    def test_register_duplicate_username(self, client: TestClient) -> None:
        client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "secret123",
        })
        response = client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "email": "other@example.com",
            "password": "secret456",
        })
        assert response.status_code == 409

    def test_login_success(self, client: TestClient) -> None:
        client.post("/api/v1/auth/register", json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "mypassword",
        })
        response = client.post("/api/v1/auth/login", json={
            "username": "loginuser",
            "password": "mypassword",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient) -> None:
        client.post("/api/v1/auth/register", json={
            "username": "wrongpw",
            "email": "wp@example.com",
            "password": "correct",
        })
        response = client.post("/api/v1/auth/login", json={
            "username": "wrongpw",
            "password": "incorrect",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient) -> None:
        response = client.post("/api/v1/auth/login", json={
            "username": "nobody",
            "password": "whatever",
        })
        assert response.status_code == 401

    def test_protected_route_without_token(self, client: TestClient) -> None:
        response = client.get("/api/v1/budgets")
        assert response.status_code == 401

    def test_protected_route_with_valid_token(self, client: TestClient) -> None:
        client.post("/api/v1/auth/register", json={
            "username": "authuser",
            "email": "auth@example.com",
            "password": "pass123",
        })
        login_resp = client.post("/api/v1/auth/login", json={
            "username": "authuser",
            "password": "pass123",
        })
        token = login_resp.json()["access_token"]
        response = client.get(
            "/api/v1/budgets",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
