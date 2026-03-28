"""Business logic for user management (S003)."""
import secrets
import string

from django.core.exceptions import ValidationError

from apps.audit.services import log_event
from apps.users.models import User, UserRole


def generate_password(length: int = 12) -> str:
    """Generate a random password with letters, digits, and punctuation."""
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def create_user(
    *,
    email: str,
    first_name: str,
    last_name: str,
    role: str,
    phone: str = "",
    password: str | None = None,
    actor: User | None = None,
) -> tuple[User, str]:
    """
    Create an agency user (admin or clerk).
    Returns (user, plain_password).
    """
    if role not in (UserRole.ADMIN, UserRole.CLERK):
        raise ValidationError("Only admin or clerk roles can be created here.")

    plain_password = password or generate_password()

    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role,
        phone=phone,
    )
    user.set_password(plain_password)
    user.full_clean()
    user.save()

    log_event(
        action="user_created",
        actor=actor,
        target_type="user",
        target_id=str(user.pk),
        detail={
            "email": user.email,
            "role": user.role,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    )

    return user, plain_password


def update_user(
    *,
    user: User,
    actor: User,
    **fields,
) -> User:
    """
    Update an agency user. Prevents admin from changing their own role.
    """
    changes = {}

    if "role" in fields and user.pk == actor.pk:
        raise ValidationError("You cannot change your own role.")

    allowed_fields = ("first_name", "last_name", "phone", "role", "is_active")
    for field in allowed_fields:
        if field in fields and getattr(user, field) != fields[field]:
            changes[field] = {
                "old": getattr(user, field),
                "new": fields[field],
            }
            setattr(user, field, fields[field])

    if changes:
        user.full_clean()
        user.save()

        action = "user_deactivated" if ("is_active" in changes and not user.is_active) else "user_updated"
        log_event(
            action=action,
            actor=actor,
            target_type="user",
            target_id=str(user.pk),
            detail={"changes": changes, "email": user.email},
        )

    return user


def reset_user_password(*, user: User, actor: User) -> str:
    """Reset password for a user. Returns the new plain password."""
    new_password = generate_password()
    user.set_password(new_password)
    user.save(update_fields=["password"])

    log_event(
        action="password_reset",
        actor=actor,
        target_type="user",
        target_id=str(user.pk),
        detail={"target_email": user.email},
    )

    return new_password
