"""Contract & document management model (S007)."""
import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import AuditMixin


class ContractType(models.TextChoices):
    SERVICE_AGREEMENT = "service_agreement", "Service Agreement"
    NDA = "nda", "NDA"
    CONTRACTOR_AGREEMENT = "contractor_agreement", "Contractor Agreement"
    AMENDMENT = "amendment", "Amendment"
    OTHER = "other", "Other"


class ContractStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    EXPIRED = "expired", "Expired"
    SUPERSEDED = "superseded", "Superseded"


ALLOWED_EXTENSIONS = (".pdf", ".jpg", ".jpeg", ".png")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def contract_upload_path(instance, filename):
    """Store as media/contracts/YYYY/MM/{uuid}_{original}."""
    from django.utils import timezone

    now = timezone.now()
    safe_name = filename.replace(" ", "_")
    return f"contracts/{now.year}/{now.month:02d}/{instance.id}_{safe_name}"


class Contract(AuditMixin):
    """
    Uploaded contract / legal document.
    Can be linked to a contractor, client, or placement (all optional).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    contract_type = models.CharField(
        max_length=30,
        choices=ContractType.choices,
        default=ContractType.OTHER,
    )
    contractor = models.ForeignKey(
        "contractors.Contractor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contracts",
    )
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contracts",
    )
    # Placement FK — left as CharField placeholder until placements app exists
    # Will be converted to FK when S006 lands.
    placement_id = models.UUIDField(null=True, blank=True)

    document = models.FileField(upload_to=contract_upload_path)
    file_name = models.CharField(max_length=255, help_text="Original filename")
    file_size = models.PositiveIntegerField(help_text="File size in bytes")

    signed_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ContractStatus.choices,
        default=ContractStatus.DRAFT,
    )
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-signed_date", "-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_contract_type_display()})"

    def clean(self):
        super().clean()
        if not self.title or not self.title.strip():
            raise ValidationError({"title": "Title is required."})
        if not self.signed_date:
            raise ValidationError({"signed_date": "Signed date is required."})
        if self.document:
            ext = os.path.splitext(self.document.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise ValidationError(
                    {"document": f"File type not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}"}
                )
            if self.document.size and self.document.size > MAX_FILE_SIZE:
                raise ValidationError(
                    {"document": f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)} MB."}
                )
