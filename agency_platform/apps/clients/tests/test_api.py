"""Tests for Client API endpoints (S005)."""
import pytest
from django.test import Client as TestClient

from apps.audit.models import AuditLog
from apps.clients.models import Client
from apps.users.models import User, UserRole


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email="admin@agency.test",
        password="testpass123",
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
    )


@pytest.fixture
def clerk_user(db):
    return User.objects.create_user(
        email="clerk@agency.test",
        password="testpass123",
        first_name="Clerk",
        last_name="User",
        role=UserRole.CLERK,
    )


@pytest.fixture
def contractor_user(db):
    return User.objects.create_user(
        email="contractor@agency.test",
        password="testpass123",
        first_name="Contractor",
        last_name="User",
        role=UserRole.CONTRACTOR,
    )


@pytest.fixture
def api_client():
    return TestClient()


@pytest.fixture
def sample_client(db, admin_user):
    from apps.clients.services import create_client

    return create_client(
        company_name="Acme Corp",
        billing_address="123 Main St",
        contact_name="John Doe",
        contact_email="john@acme.test",
        actor=admin_user,
    )


@pytest.mark.django_db
class TestClientListAPI:
    def test_admin_can_list(self, api_client, admin_user, sample_client):
        api_client.login(username="admin@agency.test", password="testpass123")
        resp = api_client.get("/api/clients/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["company_name"] == "Acme Corp"

    def test_clerk_gets_403(self, api_client, clerk_user):
        api_client.login(username="clerk@agency.test", password="testpass123")
        resp = api_client.get("/api/clients/")
        assert resp.status_code == 403

    def test_contractor_gets_403(self, api_client, contractor_user):
        api_client.login(username="contractor@agency.test", password="testpass123")
        resp = api_client.get("/api/clients/")
        assert resp.status_code == 403

    def test_unauthenticated_gets_403(self, api_client):
        resp = api_client.get("/api/clients/")
        assert resp.status_code == 403

    def test_search_filter(self, api_client, admin_user, sample_client):
        api_client.login(username="admin@agency.test", password="testpass123")
        resp = api_client.get("/api/clients/?search=Acme")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

        resp = api_client.get("/api/clients/?search=Nonexistent")
        assert len(resp.json()) == 0


@pytest.mark.django_db
class TestClientCreateAPI:
    def test_admin_can_create(self, api_client, admin_user):
        api_client.login(username="admin@agency.test", password="testpass123")
        resp = api_client.post(
            "/api/clients/",
            data={
                "company_name": "New Corp",
                "billing_address": "456 Oak Ave",
                "contact_name": "Jane Doe",
            },
            content_type="application/json",
        )
        assert resp.status_code == 201
        assert resp.json()["company_name"] == "New Corp"
        assert Client.objects.filter(company_name="New Corp").exists()

    def test_clerk_gets_403(self, api_client, clerk_user):
        api_client.login(username="clerk@agency.test", password="testpass123")
        resp = api_client.post(
            "/api/clients/",
            data={
                "company_name": "New Corp",
                "billing_address": "456 Oak Ave",
            },
            content_type="application/json",
        )
        assert resp.status_code == 403

    def test_missing_required_fields(self, api_client, admin_user):
        api_client.login(username="admin@agency.test", password="testpass123")
        resp = api_client.post(
            "/api/clients/",
            data={"company_name": "New Corp"},
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_creates_audit_log(self, api_client, admin_user):
        api_client.login(username="admin@agency.test", password="testpass123")
        api_client.post(
            "/api/clients/",
            data={
                "company_name": "Audit Test Corp",
                "billing_address": "789 Elm St",
            },
            content_type="application/json",
        )
        log = AuditLog.objects.filter(
            action="client_created",
            detail__company_name="Audit Test Corp",
        ).first()
        assert log is not None


@pytest.mark.django_db
class TestClientDetailAPI:
    def test_admin_can_retrieve(self, api_client, admin_user, sample_client):
        api_client.login(username="admin@agency.test", password="testpass123")
        resp = api_client.get(f"/api/clients/{sample_client.pk}/")
        assert resp.status_code == 200
        assert resp.json()["company_name"] == "Acme Corp"
        assert resp.json()["billing_address"] == "123 Main St"

    def test_clerk_gets_403(self, api_client, clerk_user, sample_client):
        api_client.login(username="clerk@agency.test", password="testpass123")
        resp = api_client.get(f"/api/clients/{sample_client.pk}/")
        assert resp.status_code == 403


@pytest.mark.django_db
class TestClientUpdateAPI:
    def test_admin_can_patch(self, api_client, admin_user, sample_client):
        api_client.login(username="admin@agency.test", password="testpass123")
        resp = api_client.patch(
            f"/api/clients/{sample_client.pk}/",
            data={"company_name": "Acme Inc"},
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.json()["company_name"] == "Acme Inc"

    def test_clerk_gets_403(self, api_client, clerk_user, sample_client):
        api_client.login(username="clerk@agency.test", password="testpass123")
        resp = api_client.patch(
            f"/api/clients/{sample_client.pk}/",
            data={"company_name": "Acme Inc"},
            content_type="application/json",
        )
        assert resp.status_code == 403

    def test_deactivation_via_patch(self, api_client, admin_user, sample_client):
        api_client.login(username="admin@agency.test", password="testpass123")
        resp = api_client.patch(
            f"/api/clients/{sample_client.pk}/",
            data={"is_active": False},
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

        log = AuditLog.objects.filter(action="client_deactivated").first()
        assert log is not None
