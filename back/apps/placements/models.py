from django.db import models

from apps.clients.models import Client
from apps.contractors.models import Contractor
from apps.core.models import AuditMixin


class Placement(AuditMixin):
    class ApprovalMode(models.TextChoices):
        AGENCY_ONLY = "AGENCY_ONLY", "Agency Only"

    contractor = models.ForeignKey(
        Contractor, on_delete=models.PROTECT, related_name="placements"
    )
    client = models.ForeignKey(
        Client, on_delete=models.PROTECT, related_name="placements"
    )
    client_rate = models.DecimalField(max_digits=10, decimal_places=2)
    contractor_rate = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    approval_mode = models.CharField(
        max_length=20,
        choices=ApprovalMode.choices,
        default=ApprovalMode.AGENCY_ONLY,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "placements"

    @property
    def margin(self):
        return self.client_rate - self.contractor_rate

    def __str__(self):
        return f"{self.contractor} @ {self.client}"
