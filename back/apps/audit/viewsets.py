from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from .models import AuditLog
from .serializers import AuditLogSerializer


@extend_schema_view(
    list=extend_schema(summary="List audit logs", description="List all audit log entries (admin only)."),
    retrieve=extend_schema(summary="Get audit log", description="Retrieve an audit log entry by ID (admin only)."),
)
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]
