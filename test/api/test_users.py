"""Tests for user CRUD endpoints (admin-only)."""

import uuid
import pytest
import httpx
from utils.api_client import APIClient

API_BASE_URL = "http://192.168.0.115:8000"


class TestListUsers:
    """GET /api/users/"""

    def test_admin_lists_users(self, admin_client):
        """Admin can list all users."""
        resp = admin_client.get("/api/users/")
        assert resp.status_code == 200
        data = resp.json()
        assert "count" in data
        assert "results" in data
        assert data["count"] >= 1

    def test_list_users_unauthenticated(self):
        """Unauthenticated request returns 401."""
        resp = httpx.get(f"{API_BASE_URL}/api/users/")
        assert resp.status_code == 401

    def test_contractor_cannot_list_users(self, contractor_client):
        """Non-admin (contractor) gets 403."""
        resp = contractor_client.get("/api/users/")
        assert resp.status_code == 403


class TestCreateUser:
    """POST /api/users/"""

    def test_admin_creates_user(self, admin_client):
        """Admin can create a new user."""
        email = f"create-{uuid.uuid4().hex[:8]}@timehit.local"
        resp = admin_client.post(
            "/api/users/",
            json={
                "email": email,
                "password": "StrongPass1!",
                "role": "CONTRACTOR",
                "first_name": "New",
                "last_name": "User",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == email
        assert data["role"] == "CONTRACTOR"
        assert "id" in data
        # Cleanup
        admin_client.delete(f"/api/users/{data['id']}/")

    def test_create_user_duplicate_email(self, admin_client, created_user):
        """Creating a user with an existing email fails."""
        resp = admin_client.post(
            "/api/users/",
            json={
                "email": created_user["email"],
                "password": "StrongPass1!",
                "role": "CONTRACTOR",
                "first_name": "Dup",
                "last_name": "User",
            },
        )
        assert resp.status_code == 400

    def test_create_user_missing_required_fields(self, admin_client):
        """Missing required fields return 400."""
        resp = admin_client.post(
            "/api/users/",
            json={"email": "incomplete@timehit.local"},
        )
        assert resp.status_code == 400

    def test_create_user_invalid_role(self, admin_client):
        """Invalid role value returns 400."""
        resp = admin_client.post(
            "/api/users/",
            json={
                "email": f"badrole-{uuid.uuid4().hex[:8]}@timehit.local",
                "password": "StrongPass1!",
                "role": "SUPERADMIN",
                "first_name": "Bad",
                "last_name": "Role",
            },
        )
        assert resp.status_code == 400

    def test_contractor_cannot_create_user(self, contractor_client):
        """Non-admin (contractor) gets 403."""
        resp = contractor_client.post(
            "/api/users/",
            json={
                "email": f"sneaky-{uuid.uuid4().hex[:8]}@timehit.local",
                "password": "StrongPass1!",
                "role": "CONTRACTOR",
                "first_name": "Sneaky",
                "last_name": "User",
            },
        )
        assert resp.status_code == 403

    def test_create_user_generates_audit_entry(self, admin_client):
        """Creating a user must produce an audit log entry."""
        email = f"audit-{uuid.uuid4().hex[:8]}@timehit.local"
        resp = admin_client.post(
            "/api/users/",
            json={
                "email": email,
                "password": "StrongPass1!",
                "role": "CLERK",
                "first_name": "Audit",
                "last_name": "Test",
            },
        )
        assert resp.status_code == 201
        user_id = resp.json()["id"]

        # Check audit log
        audit_resp = admin_client.get("/api/audit-logs/")
        assert audit_resp.status_code == 200
        logs = audit_resp.json()["results"]
        create_logs = [
            e for e in logs
            if e["action"] == "user.created"
            and e["target_id"] == user_id
        ]
        assert len(create_logs) >= 1, f"No audit entry for user.created (user_id={user_id})"

        # Cleanup
        admin_client.delete(f"/api/users/{user_id}/")


class TestGetUser:
    """GET /api/users/{id}/"""

    def test_admin_gets_user_detail(self, admin_client, created_user):
        """Admin can get a user by ID."""
        resp = admin_client.get(f"/api/users/{created_user['id']}/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == created_user["email"]
        assert "is_active" in data
        assert "date_joined" in data

    def test_get_nonexistent_user(self, admin_client):
        """Getting a non-existent user returns 404."""
        resp = admin_client.get("/api/users/99999/")
        assert resp.status_code == 404

    def test_contractor_cannot_get_user(self, contractor_client, created_user):
        """Non-admin cannot access user detail."""
        resp = contractor_client.get(f"/api/users/{created_user['id']}/")
        assert resp.status_code == 403


class TestUpdateUser:
    """PATCH /api/users/{id}/"""

    def test_admin_updates_user(self, admin_client, created_user):
        """Admin can update user fields."""
        resp = admin_client.patch(
            f"/api/users/{created_user['id']}/",
            json={"first_name": "Updated"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["first_name"] == "Updated"

    def test_update_user_role(self, admin_client, created_user):
        """Admin can change a user's role."""
        resp = admin_client.patch(
            f"/api/users/{created_user['id']}/",
            json={"role": "CLERK"},
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "CLERK"

    def test_contractor_cannot_update_user(self, contractor_client, created_user):
        """Non-admin cannot update users."""
        resp = contractor_client.patch(
            f"/api/users/{created_user['id']}/",
            json={"first_name": "Hacked"},
        )
        assert resp.status_code == 403

    def test_update_generates_audit_entry(self, admin_client, created_user):
        """Updating a user must produce an audit log entry."""
        admin_client.patch(
            f"/api/users/{created_user['id']}/",
            json={"last_name": "AuditCheck"},
        )
        audit_resp = admin_client.get("/api/audit-logs/")
        assert audit_resp.status_code == 200
        logs = audit_resp.json()["results"]
        update_logs = [
            e for e in logs
            if e["action"] == "user.updated"
            and e["target_id"] == created_user["id"]
        ]
        assert len(update_logs) >= 1, "No audit entry for user.updated"


class TestDeactivateUser:
    """PATCH /api/users/{id}/ with is_active=false"""

    def test_admin_deactivates_user(self, admin_client, unique_email):
        """Admin can deactivate a user. Deactivated user cannot log in."""
        # Create a user to deactivate
        resp = admin_client.post(
            "/api/users/",
            json={
                "email": unique_email,
                "password": "TestPass123!",
                "role": "CONTRACTOR",
                "first_name": "Deactivate",
                "last_name": "Me",
            },
        )
        assert resp.status_code == 201
        user = resp.json()

        # Deactivate
        resp = admin_client.patch(
            f"/api/users/{user['id']}/",
            json={"is_active": False},
        )
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

        # Verify: deactivated user cannot log in
        login_resp = httpx.post(
            f"{API_BASE_URL}/api/auth/login/",
            json={"email": unique_email, "password": "TestPass123!"},
        )
        assert login_resp.status_code == 401

        # Cleanup
        admin_client.delete(f"/api/users/{user['id']}/")

    def test_deactivate_generates_audit_entry(self, admin_client, unique_email):
        """Deactivating a user must produce an audit log entry tracking is_active change."""
        resp = admin_client.post(
            "/api/users/",
            json={
                "email": unique_email,
                "password": "TestPass123!",
                "role": "CONTRACTOR",
                "first_name": "Audit",
                "last_name": "Deact",
            },
        )
        assert resp.status_code == 201
        user = resp.json()

        deact_resp = admin_client.patch(
            f"/api/users/{user['id']}/",
            json={"is_active": False},
        )
        assert deact_resp.status_code == 200

        audit_resp = admin_client.get("/api/audit-logs/")
        assert audit_resp.status_code == 200
        logs = audit_resp.json()["results"]

        # The backend currently records deactivation as user.updated
        # with is_active in changed_fields (not user.deactivated).
        deact_logs = [
            e for e in logs
            if e["target_id"] == user["id"]
            and e["action"] in ("user.deactivated", "user.updated")
            and (
                e["action"] == "user.deactivated"
                or (
                    isinstance(e.get("detail"), dict)
                    and "is_active" in str(e["detail"].get("changed_fields", {}))
                )
            )
        ]
        assert len(deact_logs) >= 1, (
            f"No audit entry for deactivation (user_id={user['id']}). "
            f"Found actions: {[(e['action'], e.get('detail')) for e in logs if e['target_id'] == user['id']]}"
        )

        # Cleanup
        admin_client.delete(f"/api/users/{user['id']}/")

    def test_contractor_cannot_deactivate_user(self, contractor_client, created_user):
        """Non-admin cannot deactivate users."""
        resp = contractor_client.patch(
            f"/api/users/{created_user['id']}/",
            json={"is_active": False},
        )
        assert resp.status_code == 403


class TestDeleteUser:
    """DELETE /api/users/{id}/"""

    def test_admin_deletes_user(self, admin_client, unique_email):
        """Admin can delete a user."""
        resp = admin_client.post(
            "/api/users/",
            json={
                "email": unique_email,
                "password": "TestPass123!",
                "role": "CONTRACTOR",
                "first_name": "Delete",
                "last_name": "Me",
            },
        )
        user = resp.json()

        resp = admin_client.delete(f"/api/users/{user['id']}/")
        assert resp.status_code == 204

        # Verify: user is gone
        resp = admin_client.get(f"/api/users/{user['id']}/")
        assert resp.status_code == 404

    def test_contractor_cannot_delete_user(self, contractor_client, created_user):
        """Non-admin cannot delete users."""
        resp = contractor_client.delete(f"/api/users/{created_user['id']}/")
        assert resp.status_code == 403
