"""Shared permission classes for DRF and view decorators."""
from functools import wraps

from django.http import HttpResponseForbidden
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only users with role=admin can access."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsAdminOrOwnContractor(BasePermission):
    """Admin gets full access; contractors can only access their own profile."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True
        # Contractor can only access their own profile
        return (
            request.user.role == "contractor"
            and hasattr(obj, "user")
            and obj.user_id == request.user.pk
        )


def admin_required(view_func):
    """Decorator for Django views — requires role=admin."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "admin":
            return HttpResponseForbidden("Admin access required.")
        return view_func(request, *args, **kwargs)

    return _wrapped
