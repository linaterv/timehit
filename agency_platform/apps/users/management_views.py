"""Admin UI views for user management (S003). Thin views — delegates to services."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.core.permissions import admin_required
from apps.users.models import User, UserRole
from apps.users.services import create_user, reset_user_password, update_user


@login_required
@admin_required
def user_list(request):
    """List agency users with search/filter. Supports HTMX partial."""
    qs = User.objects.filter(role__in=[UserRole.ADMIN, UserRole.CLERK])

    role = request.GET.get("role", "")
    if role in (UserRole.ADMIN, UserRole.CLERK):
        qs = qs.filter(role=role)

    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(
            Q(email__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
        )

    context = {"users": qs, "current_role": role, "search": search}

    if request.headers.get("HX-Request"):
        return render(request, "users/_partial_user_list.html", context)
    return render(request, "users/user_list.html", context)


@login_required
@admin_required
def user_create(request):
    """Create an agency user (admin/clerk)."""
    if request.method == "POST":
        try:
            user, plain_password = create_user(
                email=request.POST.get("email", "").strip(),
                first_name=request.POST.get("first_name", "").strip(),
                last_name=request.POST.get("last_name", "").strip(),
                role=request.POST.get("role", ""),
                phone=request.POST.get("phone", "").strip(),
                actor=request.user,
            )
            messages.success(
                request,
                f"User {user.email} created. Generated password: {plain_password}",
            )
            if request.headers.get("HX-Request"):
                response = HttpResponse(status=204)
                response["HX-Redirect"] = "/users/"
                return response
            return redirect("user-list")
        except ValidationError as e:
            error_messages = e.messages if hasattr(e, "messages") else [str(e)]
            context = {
                "errors": error_messages,
                "form_data": request.POST,
            }
            template = "users/_partial_user_form.html" if request.headers.get("HX-Request") else "users/user_create.html"
            return render(request, template, context)

    return render(request, "users/user_create.html")


@login_required
@admin_required
def user_edit(request, pk):
    """Edit an agency user."""
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        fields = {}
        for field in ("first_name", "last_name", "phone", "role"):
            val = request.POST.get(field)
            if val is not None:
                fields[field] = val.strip()

        is_active = request.POST.get("is_active")
        if is_active is not None:
            fields["is_active"] = is_active == "on"

        try:
            update_user(user=user, actor=request.user, **fields)
            messages.success(request, f"User {user.email} updated.")
            if request.headers.get("HX-Request"):
                response = HttpResponse(status=204)
                response["HX-Redirect"] = "/users/"
                return response
            return redirect("user-list")
        except ValidationError as e:
            error_messages = e.messages if hasattr(e, "messages") else [str(e)]
            context = {"edit_user": user, "errors": error_messages}
            template = "users/_partial_user_edit_form.html" if request.headers.get("HX-Request") else "users/user_edit.html"
            return render(request, template, context)

    is_self = user.pk == request.user.pk
    context = {"edit_user": user, "is_self": is_self}
    return render(request, "users/user_edit.html", context)


@login_required
@admin_required
@require_POST
def user_deactivate(request, pk):
    """Deactivate a user (soft delete)."""
    user = get_object_or_404(User, pk=pk)
    update_user(user=user, actor=request.user, is_active=False)
    messages.success(request, f"User {user.email} deactivated.")
    if request.headers.get("HX-Request"):
        response = HttpResponse(status=204)
        response["HX-Redirect"] = "/users/"
        return response
    return redirect("user-list")


@login_required
@admin_required
@require_POST
def user_reset_password(request, pk):
    """Reset a user's password."""
    user = get_object_or_404(User, pk=pk)
    new_password = reset_user_password(user=user, actor=request.user)
    messages.success(
        request,
        f"Password for {user.email} reset. New password: {new_password}",
    )
    if request.headers.get("HX-Request"):
        response = HttpResponse(status=204)
        response["HX-Redirect"] = f"/users/{pk}/edit/"
        return response
    return redirect("user-edit", pk=pk)
