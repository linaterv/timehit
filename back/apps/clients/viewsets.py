from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.audit.models import AuditLog
from apps.core.permissions import IsAdminOrClerk

from .models import Client
from .serializers import ClientSerializer


@extend_schema_view(
    list=extend_schema(summary="List clients", description="List all active clients (admin/clerk only). Searchable by name."),
    create=extend_schema(summary="Create client", description="Create a new client (admin/clerk only)."),
    retrieve=extend_schema(summary="Get client", description="Retrieve a client by ID (admin/clerk only)."),
    partial_update=extend_schema(summary="Update client", description="Partially update a client (admin/clerk only)."),
    destroy=extend_schema(summary="Delete client", description="Soft-delete a client (admin/clerk only)."),
)
class ClientViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrClerk]
    serializer_class = ClientSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        queryset = Client.objects.filter(is_active=True).order_by("name")
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def perform_create(self, serializer):
        client = serializer.save(created_by=self.request.user, updated_by=self.request.user)
        AuditLog.objects.create(
            actor=self.request.user,
            actor_type="User",
            actor_identifier=self.request.user.email,
            action="client.created",
            target_type="Client",
            target_id=client.id,
            detail={"name": client.name},
        )

    def perform_update(self, serializer):
        old_values = {}
        instance = serializer.instance
        for field in serializer.validated_data:
            old_values[field] = getattr(instance, field)
        client = serializer.save(updated_by=self.request.user)
        changed = {
            k: {"old": str(old_values[k]), "new": str(getattr(client, k))}
            for k in serializer.validated_data
            if old_values[k] != getattr(client, k)
        }
        AuditLog.objects.create(
            actor=self.request.user,
            actor_type="User",
            actor_identifier=self.request.user.email,
            action="client.updated",
            target_type="Client",
            target_id=client.id,
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
            action="client.deactivated",
            target_type="Client",
            target_id=instance.id,
            detail={"name": instance.name},
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
