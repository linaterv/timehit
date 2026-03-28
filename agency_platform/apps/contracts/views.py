"""Admin UI views for contract management (S007). Thin views — delegates to services."""
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from apps.clients.models import Client
from apps.contracts.models import Contract, ContractStatus, ContractType
from apps.contracts.services import create_contract, log_contract_download, update_contract
from apps.contractors.models import Contractor
from apps.core.permissions import admin_required


@login_required
@admin_required
def contract_list(request):
    """List contracts with search and filters. Supports HTMX partial."""
    qs = Contract.objects.select_related("contractor__user", "client").filter(is_active=True)

    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(
            Q(title__icontains=search)
            | Q(contractor__user__first_name__icontains=search)
            | Q(contractor__user__last_name__icontains=search)
            | Q(contractor__user__email__icontains=search)
            | Q(client__company_name__icontains=search)
        )

    contract_type = request.GET.get("contract_type", "").strip()
    if contract_type:
        qs = qs.filter(contract_type=contract_type)

    status = request.GET.get("status", "").strip()
    if status:
        qs = qs.filter(status=status)

    client_id = request.GET.get("client", "").strip()
    if client_id:
        qs = qs.filter(client_id=client_id)

    contractor_id = request.GET.get("contractor", "").strip()
    if contractor_id:
        qs = qs.filter(contractor_id=contractor_id)

    context = {
        "contracts": qs,
        "search": search,
        "selected_type": contract_type,
        "selected_status": status,
        "selected_client": client_id,
        "selected_contractor": contractor_id,
        "contract_types": ContractType.choices,
        "contract_statuses": ContractStatus.choices,
        "clients": Client.objects.filter(is_active=True).order_by("company_name"),
        "contractors": Contractor.objects.select_related("user").all(),
    }

    if request.headers.get("HX-Request"):
        return render(request, "contracts/_partial_contract_list.html", context)
    return render(request, "contracts/contract_list.html", context)


@login_required
@admin_required
def contract_create(request):
    """Upload a new contract. Standard POST — no HTMX on form submit."""
    if request.method == "POST":
        try:
            # Resolve optional FKs
            contractor = None
            contractor_id = request.POST.get("contractor", "").strip()
            if contractor_id:
                contractor = Contractor.objects.get(pk=contractor_id)

            client = None
            client_id = request.POST.get("client", "").strip()
            if client_id:
                client = Client.objects.get(pk=client_id)

            document = request.FILES.get("document")
            if not document:
                raise ValidationError({"document": "File is required."})

            contract = create_contract(
                title=request.POST.get("title", "").strip(),
                contract_type=request.POST.get("contract_type", "other"),
                document=document,
                signed_date=request.POST.get("signed_date", "").strip() or None,
                expiry_date=request.POST.get("expiry_date", "").strip() or None,
                contractor=contractor,
                client=client,
                status=request.POST.get("status", "draft"),
                notes=request.POST.get("notes", "").strip(),
                actor=request.user,
            )
            messages.success(request, f'Contract "{contract.title}" uploaded.')
            return redirect("contract-list")
        except (ValidationError, Contractor.DoesNotExist, Client.DoesNotExist) as e:
            if isinstance(e, ValidationError):
                error_messages = e.messages if hasattr(e, "messages") else [str(e)]
            else:
                error_messages = [str(e)]
            context = {
                "errors": error_messages,
                "form_data": request.POST,
                "contract_types": ContractType.choices,
                "contract_statuses": ContractStatus.choices,
                "clients": Client.objects.filter(is_active=True).order_by("company_name"),
                "contractors": Contractor.objects.select_related("user").all(),
            }
            return render(request, "contracts/contract_create.html", context)

    context = {
        "contract_types": ContractType.choices,
        "contract_statuses": ContractStatus.choices,
        "clients": Client.objects.filter(is_active=True).order_by("company_name"),
        "contractors": Contractor.objects.select_related("user").all(),
    }
    return render(request, "contracts/contract_create.html", context)


@login_required
def contract_detail(request, pk):
    """Contract detail view — admin sees all, contractor sees own only."""
    contract = get_object_or_404(
        Contract.objects.select_related("contractor__user", "client"), pk=pk
    )

    if request.user.role == "contractor":
        if not (contract.contractor and contract.contractor.user_id == request.user.pk):
            return HttpResponseForbidden("You can only view your own contracts.")
    elif request.user.role not in ("admin", "clerk"):
        return HttpResponseForbidden("Access denied.")

    is_pdf = contract.file_name.lower().endswith(".pdf")
    context = {"contract": contract, "is_pdf": is_pdf}
    return render(request, "contracts/contract_detail.html", context)


@login_required
@admin_required
def contract_edit(request, pk):
    """Edit contract metadata or replace file. Standard POST."""
    contract = get_object_or_404(
        Contract.objects.select_related("contractor__user", "client"), pk=pk
    )

    if request.method == "POST":
        try:
            fields = {}
            for field in ("title", "contract_type", "signed_date", "expiry_date", "status", "notes"):
                val = request.POST.get(field)
                if val is not None:
                    fields[field] = val.strip() if val.strip() else (None if field == "expiry_date" else val.strip())

            # Resolve FKs
            contractor_id = request.POST.get("contractor", "").strip()
            fields["contractor"] = Contractor.objects.get(pk=contractor_id) if contractor_id else None

            client_id = request.POST.get("client", "").strip()
            fields["client"] = Client.objects.get(pk=client_id) if client_id else None

            new_document = request.FILES.get("document")

            update_contract(
                contract=contract,
                actor=request.user,
                new_document=new_document,
                **fields,
            )
            messages.success(request, f'Contract "{contract.title}" updated.')
            return redirect("contract-detail", pk=contract.pk)
        except (ValidationError, Contractor.DoesNotExist, Client.DoesNotExist) as e:
            if isinstance(e, ValidationError):
                error_messages = e.messages if hasattr(e, "messages") else [str(e)]
            else:
                error_messages = [str(e)]
            context = {
                "contract": contract,
                "errors": error_messages,
                "contract_types": ContractType.choices,
                "contract_statuses": ContractStatus.choices,
                "clients": Client.objects.filter(is_active=True).order_by("company_name"),
                "contractors": Contractor.objects.select_related("user").all(),
            }
            return render(request, "contracts/contract_edit.html", context)

    context = {
        "contract": contract,
        "contract_types": ContractType.choices,
        "contract_statuses": ContractStatus.choices,
        "clients": Client.objects.filter(is_active=True).order_by("company_name"),
        "contractors": Contractor.objects.select_related("user").all(),
    }
    return render(request, "contracts/contract_edit.html", context)


@login_required
def contract_download(request, pk):
    """Download contract file. Logs download in audit."""
    contract = get_object_or_404(Contract, pk=pk)

    # Permission check
    if request.user.role == "contractor":
        if not (contract.contractor and contract.contractor.user_id == request.user.pk):
            return HttpResponseForbidden("You can only download your own contracts.")
    elif request.user.role not in ("admin", "clerk"):
        return HttpResponseForbidden("Access denied.")

    log_contract_download(contract=contract, actor=request.user)

    response = FileResponse(contract.document.open("rb"), as_attachment=True)
    response["Content-Disposition"] = f'attachment; filename="{contract.file_name}"'
    return response
