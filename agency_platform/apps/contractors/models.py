"""Contractor profile model (S004)."""
from django.conf import settings
from django.db import models

from apps.core.models import AuditMixin


class Contractor(AuditMixin):
    """
    Contractor-specific profile linked 1:1 to User (role=contractor).
    Keeps the User model clean — contractor fields live here.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contractor_profile",
    )
    company_name = models.CharField(max_length=255, blank=True)
    tax_id = models.CharField(max_length=50, blank=True, verbose_name="Tax ID")
    bank_name = models.CharField(max_length=255, blank=True)
    bank_account = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    notes = models.TextField(
        blank=True,
        help_text="Internal notes — not visible to contractor.",
    )

    class Meta:
        ordering = ["user__email"]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"
