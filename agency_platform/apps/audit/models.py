from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Explicit business-event audit log."""

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    actor_type = models.CharField(
        max_length=20,
        help_text='e.g. "user", "api_agent", "system"',
    )
    actor_identifier = models.CharField(
        max_length=255,
        help_text="Email, token name, or 'system'",
    )
    action = models.CharField(max_length=100, db_index=True)
    target_type = models.CharField(max_length=100, blank=True, default="")
    target_id = models.CharField(max_length=255, null=True, blank=True)
    detail = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.actor_identifier} → {self.action}"
