"""E2E test fixtures."""

from __future__ import annotations

import uuid
import pytest
import httpx
from playwright.sync_api import Page

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
def admin_api_token():
    """Get a fresh admin JWT access token from the API."""
    resp = httpx.post(
        f"{API_BASE_URL}/api/auth/login/",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200
    return resp.json()["access"]


@pytest.fixture()
def unique_email():
    return f"e2e-{uuid.uuid4().hex[:8]}@timehit.local"


@pytest.fixture()
def created_e2e_user(admin_api_token, unique_email):
    """Create a test user via API for E2E tests, clean up after."""
    resp = httpx.post(
        f"{API_BASE_URL}/api/users/",
        json={
            "email": unique_email,
            "password": "TestPass123!",
            "role": "CONTRACTOR",
            "first_name": "E2ETest",
            "last_name": "User",
        },
        headers={"Authorization": f"Bearer {admin_api_token}"},
    )
    assert resp.status_code == 201
    user = resp.json()
    yield user
    httpx.delete(
        f"{API_BASE_URL}/api/users/{user['id']}/",
        headers={"Authorization": f"Bearer {admin_api_token}"},
    )


@pytest.fixture()
def logged_in_admin(page: Page):
    """Log in as admin via the UI and navigate to dashboard.

    Tokens are stored in-memory by the frontend — use client-side navigation
    (sidebar clicks) after this, NOT page.goto().
    """
    page.goto("/login")
    page.get_by_test_id("email-input").wait_for(state="visible", timeout=10000)
    page.get_by_test_id("email-input").fill(ADMIN_EMAIL)
    page.get_by_test_id("password-input").fill(ADMIN_PASSWORD)
    page.get_by_test_id("login-button").click()
    page.wait_for_url("**/dashboard**", timeout=10000)
    return page
