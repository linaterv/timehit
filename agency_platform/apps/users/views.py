from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.audit.services import log_event


def get_client_ip(request):
    """Extract client IP from request."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR", "")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        ip = get_client_ip(request)

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            log_event(
                action="login_success",
                actor=user,
                actor_type="user",
                target_type="session",
                detail={"ip": ip},
            )
            next_url = request.GET.get("next", "dashboard")
            return redirect(next_url)
        else:
            log_event(
                action="login_failure",
                actor_type="user",
                actor_identifier=email,
                target_type="session",
                detail={"ip": ip},
            )
            messages.error(request, "Invalid email or password.")

    return render(request, "users/login.html")


@require_POST
@login_required
def logout_view(request):
    ip = get_client_ip(request)
    log_event(
        action="logout",
        actor=request.user,
        actor_type="user",
        target_type="session",
        detail={"ip": ip},
    )
    logout(request)
    return redirect("login")


@login_required
def dashboard_view(request):
    return render(request, "users/dashboard.html")
