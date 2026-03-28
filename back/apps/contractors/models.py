from django.conf import settings
from django.db import models

from apps.core.models import AuditMixin


class Contractor(AuditMixin):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contractor_profile",
    )
    hourly_rate_default = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    phone = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "contractors"

    def __str__(self):
        return self.user.get_full_name() or self.user.email
