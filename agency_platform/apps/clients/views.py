"""Admin UI views for client management (S005). Thin views — delegates to services."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.clients.models import Client
from apps.clients.services import create_client, update_client
from apps.core.permissions import admin_required


@login_required
@admin_required
def client_list(request):
    """List clients with search/filter. Supports HTMX partial."""
    qs = Client.objects.all()

    # Filter by active/inactive
    status_filter = request.GET.get("status", "")
    if status_filter == "active":
        qs = qs.filter(is_active=True)
    elif status_filter == "inactive":
        qs = qs.filter(is_active=False)

    # Search by company name or contact name
    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(
            Q(company_name__icontains=search)
            | Q(contact_name__icontains=search)
        )

    context = {
        "clients": qs,
        "search": search,
        "current_status": status_filter,
    }

    if request.headers.get("HX-Request"):
        return render(request, "clients/_partial_client_list.html", context)
    return render(request, "clients/client_list.html", context)


@login_required
@admin_required
def client_create(request):
    """Create a new client."""
    if request.method == "POST":
        try:
            payment_terms_raw = request.POST.get("payment_terms", "30").strip()
            try:
                payment_terms = int(payment_terms_raw)
            except (ValueError, TypeError):
                payment_terms = 30

            client = create_client(
                company_name=request.POST.get("company_name", "").strip(),
                billing_address=request.POST.get("billing_address", "").strip(),
                tax_id=request.POST.get("tax_id", "").strip(),
                contact_name=request.POST.get("contact_name", "").strip(),
                contact_email=request.POST.get("contact_email", "").strip(),
                contact_phone=request.POST.get("contact_phone", "").strip(),
                payment_terms=payment_terms,
                notes=request.POST.get("notes", "").strip(),
                actor=request.user,
            )
            messages.success(
                request, f"Client '{client.company_name}' created."
            )
            if request.headers.get("HX-Request"):
                response = HttpResponse(status=204)
                response["HX-Redirect"] = "/clients/"
                return response
            return redirect("client-list")
        except ValidationError as e:
            error_messages = (
                e.messages
                if hasattr(e, "messages")
                else [str(e)]
            )
            context = {"errors": error_messages, "form_data": request.POST}
            template = (
                "clients/_partial_client_form.html"
                if request.headers.get("HX-Request")
                else "clients/client_create.html"
            )
            return render(request, template, context)

    return render(request, "clients/client_create.html")


@login_required
@admin_required
def client_edit(request, pk):
    """Edit a client."""
    client = get_object_or_404(Client, pk=pk)

    if request.method == "POST":
        fields = {}
        for field in (
            "company_name",
            "billing_address",
            "tax_id",
            "contact_name",
            "contact_email",
            "contact_phone",
            "notes",
        ):
            val = request.POST.get(field)
            if val is not None:
                fields[field] = val.strip()

        payment_terms_raw = request.POST.get("payment_terms")
        if payment_terms_raw is not None:
            try:
                fields["payment_terms"] = int(payment_terms_raw.strip())
            except (ValueError, TypeError):
                pass

        is_active = request.POST.get("is_active")
        if is_active is not None:
            fields["is_active"] = is_active == "on"

        try:
            update_client(client=client, actor=request.user, **fields)
            messages.success(
                request, f"Client '{client.company_name}' updated."
            )
            if request.headers.get("HX-Request"):
                response = HttpResponse(status=204)
                response["HX-Redirect"] = "/clients/"
                return response
            return redirect("client-list")
        except ValidationError as e:
            error_messages = (
                e.messages
                if hasattr(e, "messages")
                else [str(e)]
            )
            context = {"client": client, "errors": error_messages}
            template = (
                "clients/_partial_client_edit_form.html"
                if request.headers.get("HX-Request")
                else "clients/client_edit.html"
            )
            return render(request, template, context)

    context = {"client": client}
    return render(request, "clients/client_edit.html", context)


@login_required
@admin_required
@require_POST
def client_deactivate(request, pk):
    """Deactivate a client."""
    client = get_object_or_404(Client, pk=pk)
    update_client(client=client, actor=request.user, is_active=False)
    messages.success(request, f"Client '{client.company_name}' deactivated.")
    if request.headers.get("HX-Request"):
        response = HttpResponse(status=204)
        response["HX-Redirect"] = "/clients/"
        return response
    return redirect("client-list")
