"""Tests for Client model (S005)."""
import pytest
from django.core.exceptions import ValidationError

from apps.clients.models import Client


@pytest.mark.django_db
class TestClientModel:
    def test_create_valid_client(self):
        client = Client(
            company_name="Acme Corp",
            billing_address="123 Main St, City",
        )
        client.full_clean()
        client.save()
        assert client.pk is not None
        assert client.is_active is True
        assert client.payment_terms == 30

    def test_company_name_required(self):
        client = Client(
            company_name="",
            billing_address="123 Main St",
        )
        with pytest.raises(ValidationError) as exc_info:
            client.full_clean()
        assert "company_name" in str(exc_info.value)

    def test_billing_address_required(self):
        client = Client(
            company_name="Acme Corp",
            billing_address="",
        )
        with pytest.raises(ValidationError) as exc_info:
            client.full_clean()
        assert "billing_address" in str(exc_info.value)

    def test_whitespace_only_company_name_rejected(self):
        client = Client(
            company_name="   ",
            billing_address="123 Main St",
        )
        with pytest.raises(ValidationError):
            client.full_clean()

    def test_whitespace_only_billing_address_rejected(self):
        client = Client(
            company_name="Acme Corp",
            billing_address="   ",
        )
        with pytest.raises(ValidationError):
            client.full_clean()

    def test_default_payment_terms(self):
        client = Client(
            company_name="Acme Corp",
            billing_address="123 Main St",
        )
        assert client.payment_terms == 30

    def test_uuid_primary_key(self):
        client = Client(
            company_name="Acme Corp",
            billing_address="123 Main St",
        )
        client.full_clean()
        client.save()
        import uuid

        assert isinstance(client.pk, uuid.UUID)

    def test_str_representation(self):
        client = Client(company_name="Acme Corp", billing_address="Addr")
        assert str(client) == "Acme Corp"

    def test_optional_fields_blank(self):
        client = Client(
            company_name="Acme Corp",
            billing_address="123 Main St",
            tax_id="",
            contact_name="",
            contact_email="",
            contact_phone="",
            notes="",
        )
        client.full_clean()
        client.save()
        assert client.pk is not None

    def test_invalid_contact_email(self):
        client = Client(
            company_name="Acme Corp",
            billing_address="123 Main St",
            contact_email="not-an-email",
        )
        with pytest.raises(ValidationError):
            client.full_clean()
