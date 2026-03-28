"""API test fixtures."""

import uuid
import pytest
from utils.api_client import APIClient

API_BASE_URL = "http://192.168.0.115:8000"
ADMIN_EMAIL = "admin@timehit.local"
ADMIN_PASSWORD = "admin"


@pytest.fixture(scope="session")
def admin_client() -> APIClient:
    """Authenticated admin API client (session-scoped)."""
    client = APIClient(API_BASE_URL)
    data = client.login(ADMIN_EMAIL, ADMIN_PASSWORD)
    assert client.access_token, f"Admin login failed: {data}"
    yield client
    client.close()


@pytest.fixture()
def unique_email() -> str:
    """Generate a unique email for test user creation."""
    return f"test-{uuid.uuid4().hex[:8]}@timehit.local"


@pytest.fixture()
def created_user(admin_client, unique_email):
    """Create a test user via API and clean up after test."""
    resp = admin_client.post(
        "/api/users/",
        json={
            "email": unique_email,
            "password": "TestPass123!",
            "role": "CONTRACTOR",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    assert resp.status_code == 201, f"User creation failed: {resp.text}"
    user = resp.json()
    yield user
    # Cleanup: delete the user
    admin_client.delete(f"/api/users/{user['id']}/")


@pytest.fixture()
def contractor_client(created_user) -> APIClient:
    """Authenticated contractor API client."""
    client = APIClient(API_BASE_URL)
    data = client.login(created_user["email"], "TestPass123!")
    assert client.access_token, f"Contractor login failed: {data}"
    yield client
    client.close()
