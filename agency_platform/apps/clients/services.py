"""Business logic for client management (S005)."""
from apps.audit.services import log_event
from apps.clients.models import Client
from apps.users.models import User


def create_client(
    *,
    company_name: str,
    billing_address: str,
    tax_id: str = "",
    contact_name: str = "",
    contact_email: str = "",
    contact_phone: str = "",
    payment_terms: int = 30,
    notes: str = "",
    actor: User | None = None,
) -> Client:
    """Create a new client company. Returns the Client instance."""
    client = Client(
        company_name=company_name,
        billing_address=billing_address,
        tax_id=tax_id,
        contact_name=contact_name,
        contact_email=contact_email,
        contact_phone=contact_phone,
        payment_terms=payment_terms,
        notes=notes,
    )
    client.full_clean()
    client.save()

    log_event(
        action="client_created",
        actor=actor,
        target_type="client",
        target_id=str(client.pk),
        detail={
            "company_name": client.company_name,
        },
    )

    return client


def update_client(
    *,
    client: Client,
    actor: User,
    **fields,
) -> Client:
    """
    Update a client. Tracks changes for audit log.
    """
    changes = {}

    allowed_fields = (
        "company_name",
        "billing_address",
        "tax_id",
        "contact_name",
        "contact_email",
        "contact_phone",
        "payment_terms",
        "notes",
        "is_active",
    )

    for field in allowed_fields:
        if field in fields and getattr(client, field) != fields[field]:
            changes[field] = {
                "old": getattr(client, field),
                "new": fields[field],
            }
            setattr(client, field, fields[field])

    if changes:
        client.full_clean()
        client.save()

        if "is_active" in changes and not client.is_active:
            action = "client_deactivated"
        else:
            action = "client_updated"

        log_event(
            action=action,
            actor=actor,
            target_type="client",
            target_id=str(client.pk),
            detail={
                "changes": changes,
                "company_name": client.company_name,
            },
        )

    return client
