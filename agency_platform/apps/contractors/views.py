"""Admin UI views for contractor management (S004). Thin views — delegates to services."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.contractors.models import Contractor
from apps.contractors.services import create_contractor, update_contractor
from apps.core.permissions import admin_required


@login_required
@admin_required
def contractor_list(request):
    """List contractors with search. Supports HTMX partial."""
    qs = Contractor.objects.select_related("user").all()

    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(
            Q(user__email__icontains=search)
            | Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(company_name__icontains=search)
        )

    context = {"contractors": qs, "search": search}

    if request.headers.get("HX-Request"):
        return render(request, "contractors/_partial_contractor_list.html", context)
    return render(request, "contractors/contractor_list.html", context)


@login_required
@admin_required
def contractor_create(request):
    """Create a contractor (user + profile in one step)."""
    if request.method == "POST":
        try:
            contractor, plain_password = create_contractor(
                email=request.POST.get("email", "").strip(),
                first_name=request.POST.get("first_name", "").strip(),
                last_name=request.POST.get("last_name", "").strip(),
                phone=request.POST.get("phone", "").strip(),
                company_name=request.POST.get("company_name", "").strip(),
                tax_id=request.POST.get("tax_id", "").strip(),
                bank_name=request.POST.get("bank_name", "").strip(),
                bank_account=request.POST.get("bank_account", "").strip(),
                address=request.POST.get("address", "").strip(),
                notes=request.POST.get("notes", "").strip(),
                actor=request.user,
            )
            messages.success(
                request,
                f"Contractor {contractor.user.email} created. Generated password: {plain_password}",
            )
            if request.headers.get("HX-Request"):
                response = HttpResponse(status=204)
                response["HX-Redirect"] = "/contractors/"
                return response
            return redirect("contractor-list")
        except ValidationError as e:
            error_messages = e.messages if hasattr(e, "messages") else [str(e)]
            context = {"errors": error_messages, "form_data": request.POST}
            template = (
                "contractors/_partial_contractor_form.html"
                if request.headers.get("HX-Request")
                else "contractors/contractor_create.html"
            )
            return render(request, template, context)

    return render(request, "contractors/contractor_create.html")


@login_required
@admin_required
def contractor_edit(request, pk):
    """Edit a contractor."""
    contractor = get_object_or_404(Contractor.objects.select_related("user"), pk=pk)

    if request.method == "POST":
        fields = {}
        for field in ("first_name", "last_name", "phone", "company_name", "tax_id",
                       "bank_name", "bank_account", "address", "notes"):
            val = request.POST.get(field)
            if val is not None:
                fields[field] = val.strip()

        is_active = request.POST.get("is_active")
        if is_active is not None:
            fields["is_active"] = is_active == "on"

        try:
            update_contractor(contractor=contractor, actor=request.user, **fields)
            messages.success(request, f"Contractor {contractor.user.email} updated.")
            if request.headers.get("HX-Request"):
                response = HttpResponse(status=204)
                response["HX-Redirect"] = "/contractors/"
                return response
            return redirect("contractor-list")
        except ValidationError as e:
            error_messages = e.messages if hasattr(e, "messages") else [str(e)]
            context = {"contractor": contractor, "errors": error_messages}
            template = (
                "contractors/_partial_contractor_edit_form.html"
                if request.headers.get("HX-Request")
                else "contractors/contractor_edit.html"
            )
            return render(request, template, context)

    context = {"contractor": contractor}
    return render(request, "contractors/contractor_edit.html", context)


@login_required
@admin_required
@require_POST
def contractor_deactivate(request, pk):
    """Deactivate a contractor."""
    contractor = get_object_or_404(Contractor.objects.select_related("user"), pk=pk)
    update_contractor(contractor=contractor, actor=request.user, is_active=False)
    messages.success(request, f"Contractor {contractor.user.email} deactivated.")
    if request.headers.get("HX-Request"):
        response = HttpResponse(status=204)
        response["HX-Redirect"] = "/contractors/"
        return response
    return redirect("contractor-list")


@login_required
def contractor_own_profile(request):
    """Contractor views/edits their own profile."""
    if request.user.role != "contractor":
        return HttpResponseForbidden("Contractors only.")

    try:
        contractor = Contractor.objects.select_related("user").get(user=request.user)
    except Contractor.DoesNotExist:
        return HttpResponseForbidden("No contractor profile found.")

    if request.method == "POST":
        fields = {}
        for field in ("phone", "bank_name", "bank_account", "address"):
            val = request.POST.get(field)
            if val is not None:
                fields[field] = val.strip()

        try:
            update_contractor(contractor=contractor, actor=request.user, **fields)
            messages.success(request, "Profile updated.")
            if request.headers.get("HX-Request"):
                response = HttpResponse(status=204)
                response["HX-Redirect"] = "/contractors/my-profile/"
                return response
            return redirect("contractor-own-profile")
        except ValidationError as e:
            error_messages = e.messages if hasattr(e, "messages") else [str(e)]
            context = {"contractor": contractor, "errors": error_messages}
            return render(request, "contractors/contractor_own_profile.html", context)

    context = {"contractor": contractor}
    return render(request, "contractors/contractor_own_profile.html", context)
