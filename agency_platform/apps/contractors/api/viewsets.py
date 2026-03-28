"""DRF viewsets for Contractor management (S004)."""
from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.contractors.api.serializers import (
    ContractorCreateSerializer,
    ContractorDetailSerializer,
    ContractorListSerializer,
    ContractorOwnProfileSerializer,
    ContractorSelfUpdateSerializer,
    ContractorUpdateSerializer,
)
from apps.contractors.models import Contractor
from apps.contractors.services import create_contractor, update_contractor
from apps.core.permissions import IsAdminOrOwnContractor


class ContractorViewSet(viewsets.ViewSet):
    """
    POST   /api/contractors/       — create (admin only)
    GET    /api/contractors/       — list (admin only)
    GET    /api/contractors/{id}/ — detail (admin: full; contractor: own only)
    PATCH  /api/contractors/{id}/ — update (admin: all fields; contractor: limited)
    """

    permission_classes = [IsAdminOrOwnContractor]

    def _get_contractor(self, pk):
        try:
            return Contractor.objects.select_related("user").get(pk=pk)
        except (Contractor.DoesNotExist, ValueError):
            return None

    def list(self, request):
        if request.user.role != "admin":
            # Contractors see only their own profile in list form
            try:
                own = Contractor.objects.select_related("user").get(user=request.user)
                return Response(ContractorListSerializer([own], many=True).data)
            except Contractor.DoesNotExist:
                return Response([])

        qs = Contractor.objects.select_related("user").all()

        search = request.query_params.get("search", "").strip()
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(user__email__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(company_name__icontains=search)
            )

        serializer = ContractorListSerializer(qs, many=True)
        return Response(serializer.data)

    def create(self, request):
        if request.user.role != "admin":
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = ContractorCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            contractor, plain_password = create_contractor(
                actor=request.user,
                **serializer.validated_data,
            )
        except ValidationError as e:
            return Response(
                {"detail": e.messages if hasattr(e, "messages") else str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = ContractorDetailSerializer(contractor).data
        data["generated_password"] = plain_password
        return Response(data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        contractor = self._get_contractor(pk)
        if not contractor:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Check object permission
        self.check_object_permissions(request, contractor)

        if request.user.role == "admin":
            serializer = ContractorDetailSerializer(contractor)
        else:
            serializer = ContractorOwnProfileSerializer(contractor)

        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        contractor = self._get_contractor(pk)
        if not contractor:
            return Response(status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, contractor)

        if request.user.role == "admin":
            serializer = ContractorUpdateSerializer(data=request.data)
        else:
            # Contractor can only edit limited fields
            serializer = ContractorSelfUpdateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        try:
            contractor = update_contractor(
                contractor=contractor,
                actor=request.user,
                **serializer.validated_data,
            )
        except ValidationError as e:
            return Response(
                {"detail": e.messages if hasattr(e, "messages") else str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.role == "admin":
            return Response(ContractorDetailSerializer(contractor).data)
        return Response(ContractorOwnProfileSerializer(contractor).data)

    def check_object_permissions(self, request, obj):
        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, obj):
                self.permission_denied(request)
