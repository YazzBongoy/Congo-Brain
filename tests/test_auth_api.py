"""Tests for authentication and user management API endpoints."""

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

    def test_protected_route_with_valid_token(self, client: TestClient, auth_headers: dict) -> None:
        response = client.get("/api/v1/budgets", headers=auth_headers)
        assert response.status_code == 200


class TestUserManagement:
    def test_get_current_user(self, client: TestClient, auth_headers: dict) -> None:
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["username"] == "testadmin"

    def test_list_users_admin(self, client: TestClient, auth_headers: dict) -> None:
        response = client.get("/api/v1/auth/users", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_list_users_viewer_forbidden(self, client: TestClient, viewer_headers: dict) -> None:
        response = client.get("/api/v1/auth/users", headers=viewer_headers)
        assert response.status_code == 403

    def test_update_user_role(self, client: TestClient, auth_headers: dict) -> None:
        reg = client.post("/api/v1/auth/register", json={
            "username": "updatable",
            "email": "upd@test.com",
            "password": "pass123",
            "role": "viewer",
        })
        user_id = reg.json()["id"]
        response = client.patch(
            f"/api/v1/auth/users/{user_id}",
            headers=auth_headers,
            json={"role": "analyst"},
        )
        assert response.status_code == 200
        assert response.json()["role"] == "analyst"

    def test_delete_user(self, client: TestClient, auth_headers: dict) -> None:
        reg = client.post("/api/v1/auth/register", json={
            "username": "deletable",
            "email": "del@test.com",
            "password": "pass123",
        })
        user_id = reg.json()["id"]
        response = client.delete(f"/api/v1/auth/users/{user_id}", headers=auth_headers)
        assert response.status_code == 204

    def test_viewer_cannot_delete_user(self, client: TestClient, viewer_headers: dict) -> None:
        response = client.delete("/api/v1/auth/users/1", headers=viewer_headers)
        assert response.status_code == 403

    def test_list_roles(self, client: TestClient, auth_headers: dict) -> None:
        response = client.get("/api/v1/auth/roles", headers=auth_headers)
        assert response.status_code == 200
        roles = response.json()
        assert len(roles) == 3
        role_names = {r["role"] for r in roles}
        assert role_names == {"admin", "analyst", "viewer"}
