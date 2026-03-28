"""Tests for Client service functions (S005)."""
import pytest
from django.core.exceptions import ValidationError

from apps.audit.models import AuditLog
from apps.clients.models import Client
from apps.clients.services import create_client, update_client
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


@pytest.mark.django_db
class TestCreateClient:
    def test_creates_client_successfully(self, admin_user):
        client = create_client(
            company_name="Acme Corp",
            billing_address="123 Main St, City",
            contact_name="John Doe",
            contact_email="john@acme.test",
            actor=admin_user,
        )
        assert client.pk is not None
        assert client.company_name == "Acme Corp"
        assert client.billing_address == "123 Main St, City"
        assert client.is_active is True
        assert client.payment_terms == 30

    def test_creates_audit_log(self, admin_user):
        client = create_client(
            company_name="Acme Corp",
            billing_address="123 Main St",
            actor=admin_user,
        )
        log = AuditLog.objects.filter(action="client_created").first()
        assert log is not None
        assert log.actor == admin_user
        assert log.detail["company_name"] == "Acme Corp"

    def test_rejects_empty_company_name(self, admin_user):
        with pytest.raises(ValidationError):
            create_client(
                company_name="",
                billing_address="123 Main St",
                actor=admin_user,
            )

    def test_rejects_empty_billing_address(self, admin_user):
        with pytest.raises(ValidationError):
            create_client(
                company_name="Acme Corp",
                billing_address="",
                actor=admin_user,
            )

    def test_custom_payment_terms(self, admin_user):
        client = create_client(
            company_name="Slow Pay Ltd",
            billing_address="456 Oak Ave",
            payment_terms=60,
            actor=admin_user,
        )
        assert client.payment_terms == 60


@pytest.mark.django_db
class TestUpdateClient:
    def _make_client(self, admin_user):
        return create_client(
            company_name="Acme Corp",
            billing_address="123 Main St",
            contact_name="John Doe",
            actor=admin_user,
        )

    def test_updates_fields(self, admin_user):
        client = self._make_client(admin_user)
        updated = update_client(
            client=client,
            actor=admin_user,
            company_name="Acme Inc",
            contact_name="Jane Doe",
        )
        assert updated.company_name == "Acme Inc"
        assert updated.contact_name == "Jane Doe"

    def test_update_creates_audit_log(self, admin_user):
        client = self._make_client(admin_user)
        AuditLog.objects.all().delete()

        update_client(
            client=client,
            actor=admin_user,
            company_name="Acme Inc",
        )
        log = AuditLog.objects.filter(action="client_updated").first()
        assert log is not None
        assert "company_name" in log.detail["changes"]

    def test_deactivation_logged_separately(self, admin_user):
        client = self._make_client(admin_user)
        AuditLog.objects.all().delete()

        update_client(client=client, actor=admin_user, is_active=False)
        log = AuditLog.objects.filter(action="client_deactivated").first()
        assert log is not None
        assert log.detail["company_name"] == "Acme Corp"

    def test_no_changes_no_audit(self, admin_user):
        client = self._make_client(admin_user)
        AuditLog.objects.all().delete()

        update_client(
            client=client,
            actor=admin_user,
            company_name="Acme Corp",  # same value
        )
        assert AuditLog.objects.count() == 0

    def test_update_rejects_empty_company_name(self, admin_user):
        client = self._make_client(admin_user)
        with pytest.raises(ValidationError):
            update_client(
                client=client,
                actor=admin_user,
                company_name="",
            )
