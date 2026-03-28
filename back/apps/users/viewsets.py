from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.audit.models import AuditLog
from apps.core.permissions import IsAdminRole

from .serializers import UserCreateSerializer, UserReadSerializer, UserUpdateSerializer

User = get_user_model()


@extend_schema_view(
    list=extend_schema(summary="List users", description="List all active users (admin only). Filterable by role."),
    create=extend_schema(summary="Create user", description="Create a new user (admin only)."),
    retrieve=extend_schema(summary="Get user", description="Retrieve a user by ID (admin only)."),
    partial_update=extend_schema(summary="Update user", description="Partially update a user (admin only)."),
    destroy=extend_schema(summary="Delete user", description="Soft-delete a user (admin only)."),
)
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminRole]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        queryset = User.objects.filter(is_deleted=False).order_by("id")
        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "partial_update":
            return UserUpdateSerializer
        return UserReadSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            actor_type="User",
            actor_identifier=self.request.user.email,
            action="user.created",
            target_type="User",
            target_id=user.id,
            detail={"email": user.email, "role": user.role},
        )

    def perform_update(self, serializer):
        old_values = {}
        instance = serializer.instance
        for field in serializer.validated_data:
            old_values[field] = getattr(instance, field)
        user = serializer.save()
        changed = {
            k: {"old": str(old_values[k]), "new": str(getattr(user, k))}
            for k in serializer.validated_data
            if old_values[k] != getattr(user, k)
        }
        AuditLog.objects.create(
            actor=self.request.user,
            actor_type="User",
            actor_identifier=self.request.user.email,
            action="user.updated",
            target_type="User",
            target_id=user.id,
            detail={"changed_fields": changed},
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.is_active = False
        instance.save(update_fields=["is_deleted", "is_active"])
        AuditLog.objects.create(
            actor=request.user,
            actor_type="User",
            actor_identifier=request.user.email,
            action="user.deleted",
            target_type="User",
            target_id=instance.id,
            detail={"email": instance.email},
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
