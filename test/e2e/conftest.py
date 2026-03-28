"""E2E test fixtures."""

from __future__ import annotations

import uuid
import pytest
import httpx

FRONTEND_URL = "http://192.168.0.115:3000"
API_BASE_URL = "http://192.168.0.115:8000"
ADMIN_EMAIL = "admin@timehit.local"
ADMIN_PASSWORD = "admin"


@pytest.fixture(scope="session")
def browser_context_args():
    return {
        "base_url": FRONTEND_URL,
        "viewport": {"width": 1280, "height": 720},
    }


@pytest.fixture()
def admin_tokens():
    """Get fresh admin JWT tokens from the API."""
    resp = httpx.post(
        f"{API_BASE_URL}/api/auth/login/",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200
    return resp.json()


@pytest.fixture()
def unique_email():
    return f"e2e-{uuid.uuid4().hex[:8]}@timehit.local"


@pytest.fixture()
def created_e2e_user(admin_tokens, unique_email):
    """Create a test user via API for E2E tests, clean up after."""
    token = admin_tokens["access"]
    resp = httpx.post(
        f"{API_BASE_URL}/api/users/",
        json={
            "email": unique_email,
            "password": "TestPass123!",
            "role": "CONTRACTOR",
            "first_name": "E2E",
            "last_name": "Test",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    user = resp.json()
    yield user
    httpx.delete(
        f"{API_BASE_URL}/api/users/{user['id']}/",
        headers={"Authorization": f"Bearer {token}"},
    )
