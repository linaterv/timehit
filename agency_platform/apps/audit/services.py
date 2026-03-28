"""Audit logging helpers."""
from apps.audit.models import AuditLog


def log_event(
    *,
    action: str,
    actor=None,
    actor_type: str = "user",
    actor_identifier: str = "",
    target_type: str = "",
    target_id: int | None = None,
    detail: dict | None = None,
) -> AuditLog:
    """Create an audit log entry."""
    if actor and not actor_identifier:
        actor_identifier = str(getattr(actor, "email", ""))
    return AuditLog.objects.create(
        actor=actor if (actor and hasattr(actor, "pk") and actor.pk) else None,
        actor_type=actor_type,
        actor_identifier=actor_identifier,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail or {},
    )
