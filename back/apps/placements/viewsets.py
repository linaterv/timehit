from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.audit.models import AuditLog
from apps.core.permissions import IsAdminOrClerk

from .models import Placement
from .serializers import PlacementReadSerializer, PlacementWriteSerializer


@extend_schema_view(
    list=extend_schema(summary="List placements", description="List all active placements (admin/clerk only). Filterable by client, contractor, active."),
    create=extend_schema(summary="Create placement", description="Create a new placement (admin/clerk only)."),
    retrieve=extend_schema(summary="Get placement", description="Retrieve a placement by ID (admin/clerk only)."),
    partial_update=extend_schema(summary="Update placement", description="Partially update a placement (admin/clerk only)."),
    destroy=extend_schema(summary="Delete placement", description="Soft-delete a placement (admin/clerk only)."),
)
class PlacementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrClerk]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        queryset = Placement.objects.select_related(
            "contractor__user", "client"
        ).order_by("id")

        active = self.request.query_params.get("active")
        if active is not None:
            queryset = queryset.filter(is_active=active.lower() == "true")
        else:
            queryset = queryset.filter(is_active=True)

        client_id = self.request.query_params.get("client")
        if client_id:
            queryset = queryset.filter(client_id=client_id)

        contractor_id = self.request.query_params.get("contractor")
        if contractor_id:
            queryset = queryset.filter(contractor_id=contractor_id)

        return queryset

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return PlacementWriteSerializer
        return PlacementReadSerializer

    def perform_create(self, serializer):
        placement = serializer.save(created_by=self.request.user, updated_by=self.request.user)
        AuditLog.objects.create(
            actor=self.request.user,
            actor_type="User",
            actor_identifier=self.request.user.email,
            action="placement.created",
            target_type="Placement",
            target_id=placement.id,
            detail={
                "contractor_id": placement.contractor_id,
                "client_id": placement.client_id,
            },
        )

    def perform_update(self, serializer):
        old_values = {}
        instance = serializer.instance
        for field in serializer.validated_data:
            old_values[field] = getattr(instance, field)
        placement = serializer.save(updated_by=self.request.user)
        changed = {
            k: {"old": str(old_values[k]), "new": str(getattr(placement, k))}
            for k in serializer.validated_data
            if old_values[k] != getattr(placement, k)
        }
        AuditLog.objects.create(
            actor=self.request.user,
            actor_type="User",
            actor_identifier=self.request.user.email,
            action="placement.updated",
            target_type="Placement",
            target_id=placement.id,
            detail={"changed_fields": changed},
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        AuditLog.objects.create(
            actor=request.user,
            actor_type="User",
            actor_identifier=request.user.email,
            action="placement.deactivated",
            target_type="Placement",
            target_id=instance.id,
            detail={
                "contractor_id": instance.contractor_id,
                "client_id": instance.client_id,
            },
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
