"""Tests for authentication endpoints: login, refresh, logout, me."""

import pytest
import httpx
from utils.api_client import APIClient

API_BASE_URL = "http://192.168.0.115:8000"
ADMIN_EMAIL = "admin@timehit.local"
ADMIN_PASSWORD = "admin"


class TestLogin:
    """POST /api/auth/login/"""

    def test_login_valid_credentials(self):
        """Valid email+password returns access token, refresh token, and user info."""
        client = APIClient(API_BASE_URL)
        data = client.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert "access" in data
        assert "refresh" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["role"] == "ADMIN"
        client.close()

    def test_login_wrong_password(self):
        """Wrong password returns 401."""
        resp = httpx.post(
            f"{API_BASE_URL}/api/auth/login/",
            json={"email": ADMIN_EMAIL, "password": "wrongpassword"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self):
        """Non-existent email returns 401."""
        resp = httpx.post(
            f"{API_BASE_URL}/api/auth/login/",
            json={"email": "nobody@timehit.local", "password": "whatever"},
        )
        assert resp.status_code == 401

    def test_login_missing_fields(self):
        """Missing email or password returns 400."""
        resp = httpx.post(
            f"{API_BASE_URL}/api/auth/login/",
            json={"email": ADMIN_EMAIL},
        )
        assert resp.status_code == 400

    def test_login_empty_body(self):
        """Empty body returns 400."""
        resp = httpx.post(
            f"{API_BASE_URL}/api/auth/login/",
            json={},
        )
        assert resp.status_code == 400

    def test_login_creates_audit_entry(self, admin_client):
        """Logging in must create an audit log entry with action user.login."""
        # Do a fresh login to generate an audit entry
        fresh = APIClient(API_BASE_URL)
        data = fresh.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert fresh.access_token

        # Check audit log for the login event
        resp = admin_client.get("/api/audit-logs/", params={"page": 1})
        assert resp.status_code == 200
        logs = resp.json()["results"]
        login_logs = [
            e for e in logs
            if e["action"] == "user.login"
            and e["actor_identifier"] == ADMIN_EMAIL
        ]
        assert len(login_logs) >= 1, "No audit log entry for login"
        fresh.close()


class TestRefreshToken:
    """POST /api/auth/refresh/"""

    def test_refresh_returns_new_access_token(self):
        """A valid refresh token returns a new access token."""
        client = APIClient(API_BASE_URL)
        login_data = client.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        refresh_token = login_data["refresh"]

        resp = httpx.post(
            f"{API_BASE_URL}/api/auth/refresh/",
            json={"refresh": refresh_token},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access" in data
        assert data["access"] != login_data["access"]  # new token
        client.close()

    def test_refresh_invalid_token(self):
        """An invalid refresh token returns 401."""
        resp = httpx.post(
            f"{API_BASE_URL}/api/auth/refresh/",
            json={"refresh": "invalid.token.here"},
        )
        assert resp.status_code == 401

    def test_refresh_missing_token(self):
        """Missing refresh field returns 400."""
        resp = httpx.post(
            f"{API_BASE_URL}/api/auth/refresh/",
            json={},
        )
        assert resp.status_code == 400


class TestLogout:
    """POST /api/auth/logout/"""

    def test_logout_blacklists_refresh_token(self):
        """After logout, the refresh token should no longer work."""
        client = APIClient(API_BASE_URL)
        login_data = client.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        refresh_token = login_data["refresh"]

        # Logout
        resp = client.post(
            "/api/auth/logout/",
            json={"refresh": refresh_token},
        )
        assert resp.status_code == 205

        # Try to use the blacklisted refresh token
        resp = httpx.post(
            f"{API_BASE_URL}/api/auth/refresh/",
            json={"refresh": refresh_token},
        )
        assert resp.status_code == 401
        client.close()

    def test_logout_unauthenticated(self):
        """Logout without auth returns 401."""
        resp = httpx.post(
            f"{API_BASE_URL}/api/auth/logout/",
            json={"refresh": "whatever"},
        )
        assert resp.status_code == 401


class TestMe:
    """GET /api/auth/me/"""

    def test_me_returns_current_user(self, admin_client):
        """Authenticated user gets their own profile."""
        resp = admin_client.get("/api/auth/me/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == ADMIN_EMAIL
        assert data["role"] == "ADMIN"
        assert "id" in data

    def test_me_unauthenticated(self):
        """Unauthenticated request returns 401."""
        resp = httpx.get(f"{API_BASE_URL}/api/auth/me/")
        assert resp.status_code == 401

    def test_me_contractor_sees_own_data(self, contractor_client, created_user):
        """A contractor sees their own data via /me/."""
        resp = contractor_client.get("/api/auth/me/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == created_user["email"]
        assert data["role"] == "CONTRACTOR"
