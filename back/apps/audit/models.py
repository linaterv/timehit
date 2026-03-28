from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    actor_type = models.CharField(max_length=50, default="User")
    actor_identifier = models.CharField(max_length=255, blank=True, default="")
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=100, blank=True, default="")
    target_id = models.IntegerField(null=True, blank=True)
    detail = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "audit_log"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action} by {self.actor_identifier} at {self.timestamp}"
