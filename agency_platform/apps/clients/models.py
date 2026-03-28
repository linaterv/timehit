"""Client model (S005)."""
import uuid

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import AuditMixin


class Client(AuditMixin):
    """
    Client company that the agency places contractors at.
    Holds billing info and contact details.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=255)
    billing_address = models.TextField(help_text="Used on invoices.")
    tax_id = models.CharField(
        max_length=50, blank=True, verbose_name="Tax / VAT ID"
    )
    contact_name = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    payment_terms = models.PositiveIntegerField(
        default=30,
        help_text="Days until payment due.",
    )
    notes = models.TextField(blank=True, help_text="Internal notes.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["company_name"]

    def __str__(self):
        return self.company_name

    def clean(self):
        super().clean()
        if not self.company_name or not self.company_name.strip():
            raise ValidationError({"company_name": "Company name is required."})
        if not self.billing_address or not self.billing_address.strip():
            raise ValidationError(
                {"billing_address": "Billing address is required."}
            )
