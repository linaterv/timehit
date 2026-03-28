"""Business logic for contractor management (S004)."""
from django.core.exceptions import ValidationError
from django.db import transaction

from apps.audit.services import log_event
from apps.contractors.models import Contractor
from apps.users.models import User, UserRole
from apps.users.services import generate_password


def create_contractor(
    *,
    email: str,
    first_name: str,
    last_name: str,
    phone: str = "",
    company_name: str = "",
    tax_id: str = "",
    bank_name: str = "",
    bank_account: str,
    address: str = "",
    notes: str = "",
    actor: User | None = None,
) -> tuple[Contractor, str]:
    """
    Create a User (role=contractor) and Contractor profile atomically.
    Returns (contractor, plain_password).
    """
    plain_password = generate_password()

    with transaction.atomic():
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.CONTRACTOR,
            phone=phone,
        )
        user.set_password(plain_password)
        user.full_clean()
        user.save()

        contractor = Contractor(
            user=user,
            company_name=company_name,
            tax_id=tax_id,
            bank_name=bank_name,
            bank_account=bank_account,
            address=address,
            notes=notes,
        )
        contractor.full_clean()
        contractor.save()

    log_event(
        action="contractor_created",
        actor=actor,
        target_type="contractor",
        target_id=contractor.pk,
        detail={
            "email": user.email,
            "company_name": company_name,
            "first_name": first_name,
            "last_name": last_name,
        },
    )

    return contractor, plain_password


def update_contractor(
    *,
    contractor: Contractor,
    actor: User,
    **fields,
) -> Contractor:
    """
    Update contractor profile and/or associated user fields.
    Tracks bank detail changes with special audit detail.
    """
    changes = {}
    bank_changed = False

    # User-level fields
    user = contractor.user
    user_fields = ("first_name", "last_name", "phone")
    for field in user_fields:
        if field in fields and getattr(user, field) != fields[field]:
            changes[f"user.{field}"] = {
                "old": getattr(user, field),
                "new": fields[field],
            }
            setattr(user, field, fields[field])

    # Contractor-level fields
    contractor_fields = ("company_name", "tax_id", "bank_name", "bank_account", "address", "notes")
    for field in contractor_fields:
        if field in fields and getattr(contractor, field) != fields[field]:
            old_val = getattr(contractor, field)
            new_val = fields[field]

            if field in ("bank_name", "bank_account"):
                bank_changed = True
                # Mask bank details in audit
                changes[field] = {
                    "old": _mask(old_val),
                    "new": _mask(new_val),
                }
            else:
                changes[field] = {"old": old_val, "new": new_val}
            setattr(contractor, field, new_val)

    # Handle deactivation
    if "is_active" in fields and user.is_active != fields["is_active"]:
        changes["is_active"] = {"old": user.is_active, "new": fields["is_active"]}
        user.is_active = fields["is_active"]

    if changes:
        with transaction.atomic():
            user.full_clean()
            user.save()
            contractor.full_clean()
            contractor.save()

        action = "contractor_deactivated" if ("is_active" in changes and not user.is_active) else "contractor_updated"
        if bank_changed:
            action = "contractor_bank_details_changed"

        log_event(
            action=action,
            actor=actor,
            target_type="contractor",
            target_id=contractor.pk,
            detail={"changes": changes, "email": user.email},
        )

    return contractor


def _mask(value: str) -> str:
    """Mask sensitive value, showing only last 4 chars."""
    if len(value) <= 4:
        return "****"
    return "*" * (len(value) - 4) + value[-4:]
