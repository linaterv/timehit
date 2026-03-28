"""DRF viewsets for Contract management (S007)."""
from django.core.exceptions import ValidationError
from django.http import FileResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.clients.models import Client
from apps.contracts.api.serializers import (
    ContractCreateSerializer,
    ContractDetailSerializer,
    ContractListSerializer,
    ContractUpdateSerializer,
)
from apps.contracts.models import Contract
from apps.contracts.services import create_contract, log_contract_download, update_contract
from apps.contractors.models import Contractor


class ContractViewSet(viewsets.ViewSet):
    """
    POST   /api/contracts/              — create with file upload (admin only)
    GET    /api/contracts/              — list (admin: all; contractor: own only)
    GET    /api/contracts/{id}/         — detail
    PATCH  /api/contracts/{id}/         — update (admin only)
    GET    /api/contracts/{id}/download/ — download file
    """

    def _get_contract(self, pk):
        try:
            return Contract.objects.select_related(
                "contractor__user", "client"
            ).get(pk=pk, is_active=True)
        except (Contract.DoesNotExist, ValueError):
            return None

    def _check_read_permission(self, request, contract):
        """Returns None if allowed, or an error Response."""
        if request.user.role == "admin":
            return None
        if request.user.role == "clerk":
            return None  # read-only for clerks
        if request.user.role == "contractor":
            if contract.contractor and contract.contractor.user_id == request.user.pk:
                return None
            return Response(
                {"detail": "You can only view your own contracts."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(
            {"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN
        )

    def list(self, request):
        if request.user.role == "contractor":
            qs = Contract.objects.select_related(
                "contractor__user", "client"
            ).filter(
                is_active=True,
                contractor__user=request.user,
            )
        elif request.user.role in ("admin", "clerk"):
            qs = Contract.objects.select_related(
                "contractor__user", "client"
            ).filter(is_active=True)

            # Filters
            ct = request.query_params.get("contract_type", "").strip()
            if ct:
                qs = qs.filter(contract_type=ct)
            st = request.query_params.get("status", "").strip()
            if st:
                qs = qs.filter(status=st)
            search = request.query_params.get("search", "").strip()
            if search:
                from django.db.models import Q
                qs = qs.filter(
                    Q(title__icontains=search)
                    | Q(contractor__user__first_name__icontains=search)
                    | Q(contractor__user__last_name__icontains=search)
                    | Q(client__company_name__icontains=search)
                )
        else:
            return Response(
                {"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = ContractListSerializer(qs, many=True)
        return Response(serializer.data)

    def create(self, request):
        if request.user.role != "admin":
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = ContractCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Resolve FKs
        contractor = None
        if data.get("contractor"):
            try:
                contractor = Contractor.objects.get(pk=data["contractor"])
            except Contractor.DoesNotExist:
                return Response(
                    {"contractor": ["Contractor not found."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        client = None
        if data.get("client"):
            try:
                client = Client.objects.get(pk=data["client"])
            except Client.DoesNotExist:
                return Response(
                    {"client": ["Client not found."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            contract = create_contract(
                title=data["title"],
                contract_type=data["contract_type"],
                document=data["document"],
                signed_date=data["signed_date"],
                expiry_date=data.get("expiry_date"),
                contractor=contractor,
                client=client,
                status=data.get("status", "draft"),
                notes=data.get("notes", ""),
                actor=request.user,
            )
        except ValidationError as e:
            return Response(
                {"detail": e.messages if hasattr(e, "messages") else str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            ContractDetailSerializer(contract).data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, pk=None):
        contract = self._get_contract(pk)
        if not contract:
            return Response(status=status.HTTP_404_NOT_FOUND)

        err = self._check_read_permission(request, contract)
        if err:
            return err

        serializer = ContractDetailSerializer(contract)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        if request.user.role != "admin":
            return Response(status=status.HTTP_403_FORBIDDEN)

        contract = self._get_contract(pk)
        if not contract:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ContractUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        fields = {}
        for key in ("title", "contract_type", "signed_date", "expiry_date", "status", "notes"):
            if key in data:
                fields[key] = data[key]

        # Resolve FKs
        if "contractor" in data:
            if data["contractor"]:
                try:
                    fields["contractor"] = Contractor.objects.get(pk=data["contractor"])
                except Contractor.DoesNotExist:
                    return Response(
                        {"contractor": ["Contractor not found."]},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                fields["contractor"] = None

        if "client" in data:
            if data["client"]:
                try:
                    fields["client"] = Client.objects.get(pk=data["client"])
                except Client.DoesNotExist:
                    return Response(
                        {"client": ["Client not found."]},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                fields["client"] = None

        new_document = data.get("document")

        try:
            contract = update_contract(
                contract=contract,
                actor=request.user,
                new_document=new_document,
                **fields,
            )
        except ValidationError as e:
            return Response(
                {"detail": e.messages if hasattr(e, "messages") else str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(ContractDetailSerializer(contract).data)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        contract = self._get_contract(pk)
        if not contract:
            return Response(status=status.HTTP_404_NOT_FOUND)

        err = self._check_read_permission(request, contract)
        if err:
            return err

        log_contract_download(contract=contract, actor=request.user)

        response = FileResponse(contract.document.open("rb"), as_attachment=True)
        response["Content-Disposition"] = f'attachment; filename="{contract.file_name}"'
        return response
