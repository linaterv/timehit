import pytest
from django.test import Client
from django.urls import reverse

from apps.audit.models import AuditLog
from apps.users.models import User, UserRole


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
        role=UserRole.ADMIN,
    )


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
class TestLoginView:
    def test_login_page_renders(self, client):
        resp = client.get(reverse("login"))
        assert resp.status_code == 200
        assert b"Login" in resp.content

    def test_successful_login_redirects_to_dashboard(self, client, user):
        resp = client.post(
            reverse("login"),
            {"email": "test@example.com", "password": "testpass123"},
        )
        assert resp.status_code == 302
        assert "dashboard" in resp.url

    def test_successful_login_creates_audit_log(self, client, user):
        client.post(
            reverse("login"),
            {"email": "test@example.com", "password": "testpass123"},
        )
        log = AuditLog.objects.filter(action="login_success").first()
        assert log is not None
        assert log.actor_identifier == "test@example.com"

    def test_failed_login_shows_error(self, client, user):
        resp = client.post(
            reverse("login"),
            {"email": "test@example.com", "password": "wrongpass"},
        )
        assert resp.status_code == 200
        assert b"Invalid email or password" in resp.content

    def test_failed_login_creates_audit_log(self, client, user):
        client.post(
            reverse("login"),
            {"email": "test@example.com", "password": "wrongpass"},
        )
        log = AuditLog.objects.filter(action="login_failure").first()
        assert log is not None
        assert log.actor_identifier == "test@example.com"

    def test_failed_login_no_email_leak(self, client):
        """Same error message whether email exists or not."""
        resp = client.post(
            reverse("login"),
            {"email": "nonexistent@example.com", "password": "wrongpass"},
        )
        assert b"Invalid email or password" in resp.content

    def test_authenticated_user_redirected_from_login(self, client, user):
        client.login(username="test@example.com", password="testpass123")
        resp = client.get(reverse("login"))
        assert resp.status_code == 302
        assert "dashboard" in resp.url


@pytest.mark.django_db
class TestLogoutView:
    def test_logout_post(self, client, user):
        client.login(username="test@example.com", password="testpass123")
        resp = client.post(reverse("logout"))
        assert resp.status_code == 302
        assert "login" in resp.url

    def test_logout_get_not_allowed(self, client, user):
        client.login(username="test@example.com", password="testpass123")
        resp = client.get(reverse("logout"))
        assert resp.status_code == 405

    def test_logout_creates_audit_log(self, client, user):
        client.login(username="test@example.com", password="testpass123")
        client.post(reverse("logout"))
        log = AuditLog.objects.filter(action="logout").first()
        assert log is not None
        assert log.actor_identifier == "test@example.com"


@pytest.mark.django_db
class TestDashboardView:
    def test_unauthenticated_redirects_to_login(self, client):
        resp = client.get(reverse("dashboard"))
        assert resp.status_code == 302
        assert "login" in resp.url

    def test_authenticated_sees_dashboard(self, client, user):
        client.login(username="test@example.com", password="testpass123")
        resp = client.get(reverse("dashboard"))
        assert resp.status_code == 200
        assert b"Dashboard" in resp.content
