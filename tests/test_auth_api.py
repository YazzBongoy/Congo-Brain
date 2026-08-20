"""Tests for authentication and user management API endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from congo_brain.models.user import User


class TestAuthEndpoints:
    def test_register_user(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "secret123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["role"] == "viewer"

    def test_register_rejects_privileged_role_assignment(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "attacker",
                "email": "attacker@example.com",
                "password": "secret123",
                "role": "admin",
            },
        )

        assert response.status_code == 422

    def test_register_duplicate_username(self, client: TestClient) -> None:
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "secret123",
            },
        )
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "other@example.com",
                "password": "secret456",
            },
        )
        assert response.status_code == 409

    def test_login_success(self, client: TestClient) -> None:
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "loginuser",
                "email": "login@example.com",
                "password": "mypassword",
            },
        )
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "loginuser",
                "password": "mypassword",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient) -> None:
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "wrongpw",
                "email": "wp@example.com",
                "password": "correct1",
            },
        )
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "wrongpw",
                "password": "incorrect1",
            },
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nobody",
                "password": "whatever",
            },
        )
        assert response.status_code == 401

    def test_protected_route_without_token(self, client: TestClient) -> None:
        response = client.get("/api/v1/budgets")
        assert response.status_code == 401

    def test_protected_route_with_valid_token(self, client: TestClient, auth_headers: dict) -> None:
        response = client.get("/api/v1/budgets", headers=auth_headers)
        assert response.status_code == 200


class TestUserManagement:
    def test_admin_can_create_ministry_budget_officer(self, client: TestClient, auth_headers: dict) -> None:
        response = client.post(
            "/api/v1/auth/users",
            headers=auth_headers,
            json={
                "username": "health-officer",
                "email": "health-officer@example.cd",
                "password": "strong-pass",
                "role": "ministry_budget_officer",
                "ministry": "Santé Publique",
            },
        )

        assert response.status_code == 201
        assert response.json()["role"] == "ministry_budget_officer"
        assert response.json()["ministry"] == "Santé Publique"

    def test_viewer_cannot_create_user(self, client: TestClient, viewer_headers: dict) -> None:
        response = client.post(
            "/api/v1/auth/users",
            headers=viewer_headers,
            json={
                "username": "forbidden-user",
                "email": "forbidden@example.cd",
                "password": "strong-pass",
                "role": "auditor",
            },
        )

        assert response.status_code == 403

    def test_national_budget_admin_cannot_create_platform_admin(
        self,
        client: TestClient,
        db_session: Session,
    ) -> None:
        client.post(
            "/api/v1/auth/register",
            json={"username": "national-admin", "email": "national@example.cd", "password": "strong-pass"},
        )
        actor = db_session.query(User).filter(User.username == "national-admin").one()
        actor.role = "national_budget_admin"
        db_session.commit()
        login = client.post(
            "/api/v1/auth/login",
            json={"username": "national-admin", "password": "strong-pass"},
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        response = client.post(
            "/api/v1/auth/users",
            headers=headers,
            json={
                "username": "escalated-admin",
                "email": "escalated@example.cd",
                "password": "strong-pass",
                "role": "admin",
            },
        )

        assert response.status_code == 403

    def test_national_budget_admin_cannot_promote_self_to_platform_admin(
        self,
        client: TestClient,
        db_session: Session,
    ) -> None:
        client.post(
            "/api/v1/auth/register",
            json={"username": "national-admin", "email": "national@example.cd", "password": "strong-pass"},
        )
        actor = db_session.query(User).filter(User.username == "national-admin").one()
        actor.role = "national_budget_admin"
        db_session.commit()
        login = client.post(
            "/api/v1/auth/login",
            json={"username": "national-admin", "password": "strong-pass"},
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        response = client.patch(
            f"/api/v1/auth/users/{actor.id}",
            headers=headers,
            json={"role": "admin"},
        )

        assert response.status_code == 403

    def test_admin_user_creation_rejects_unknown_role(self, client: TestClient, auth_headers: dict) -> None:
        response = client.post(
            "/api/v1/auth/users",
            headers=auth_headers,
            json={
                "username": "invalid-role-user",
                "email": "invalid-role@example.cd",
                "password": "strong-pass",
                "role": "supergod",
            },
        )

        assert response.status_code == 422

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
        reg = client.post(
            "/api/v1/auth/register",
            json={
                "username": "updatable",
                "email": "upd@test.com",
                "password": "pass1234",
            },
        )
        user_id = reg.json()["id"]
        response = client.patch(
            f"/api/v1/auth/users/{user_id}",
            headers=auth_headers,
            json={"role": "analyst"},
        )
        assert response.status_code == 200
        assert response.json()["role"] == "analyst"

    def test_delete_user(self, client: TestClient, auth_headers: dict) -> None:
        reg = client.post(
            "/api/v1/auth/register",
            json={
                "username": "deletable",
                "email": "del@test.com",
                "password": "pass1234",
            },
        )
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
        role_names = {r["role"] for r in roles}
        assert {
            "admin",
            "national_budget_admin",
            "ministry_budget_officer",
            "project_manager",
            "auditor",
            "executive_viewer",
            "public_viewer",
        }.issubset(role_names)
