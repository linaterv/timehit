from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.audit.models import AuditLog
from apps.core.permissions import IsAdminOrClerk

from .models import Contractor
from .serializers import (
    ContractorCreateSerializer,
    ContractorReadSerializer,
    ContractorUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="List contractors", description="List all active contractors (admin/clerk only)."),
    create=extend_schema(summary="Create contractor", description="Create a new contractor with user account (admin/clerk only)."),
    retrieve=extend_schema(summary="Get contractor", description="Retrieve a contractor by ID (admin/clerk only)."),
    partial_update=extend_schema(summary="Update contractor", description="Partially update a contractor (admin/clerk only)."),
    destroy=extend_schema(summary="Delete contractor", description="Soft-delete a contractor (admin/clerk only)."),
)
class ContractorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrClerk]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return Contractor.objects.filter(is_active=True).select_related("user").order_by("id")

    def get_serializer_class(self):
        if self.action == "create":
            return ContractorCreateSerializer
        if self.action == "partial_update":
            return ContractorUpdateSerializer
        return ContractorReadSerializer

    def perform_create(self, serializer):
        contractor = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            actor_type="User",
            actor_identifier=self.request.user.email,
            action="contractor.created",
            target_type="Contractor",
            target_id=contractor.id,
            detail={"email": contractor.user.email},
        )

    def perform_update(self, serializer):
        old_values = {}
        instance = serializer.instance
        for field in serializer.validated_data:
            if field == "user":
                for user_field in serializer.validated_data["user"]:
                    old_values[f"user.{user_field}"] = getattr(instance.user, user_field)
            else:
                old_values[field] = getattr(instance, field)
        contractor = serializer.save()
        changed = {}
        for field in serializer.validated_data:
            if field == "user":
                for user_field in serializer.validated_data["user"]:
                    key = f"user.{user_field}"
                    new_val = getattr(contractor.user, user_field)
                    if old_values[key] != new_val:
                        changed[key] = {"old": str(old_values[key]), "new": str(new_val)}
            else:
                new_val = getattr(contractor, field)
                if old_values[field] != new_val:
                    changed[field] = {"old": str(old_values[field]), "new": str(new_val)}
        AuditLog.objects.create(
            actor=self.request.user,
            actor_type="User",
            actor_identifier=self.request.user.email,
            action="contractor.updated",
            target_type="Contractor",
            target_id=contractor.id,
            detail={"changed_fields": changed},
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        instance.user.is_active = False
        instance.user.is_deleted = True
        instance.user.save(update_fields=["is_active", "is_deleted"])
        AuditLog.objects.create(
            actor=request.user,
            actor_type="User",
            actor_identifier=request.user.email,
            action="contractor.deactivated",
            target_type="Contractor",
            target_id=instance.id,
            detail={"email": instance.user.email},
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
