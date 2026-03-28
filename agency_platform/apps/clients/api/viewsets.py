"""DRF viewsets for Client management (S005)."""
from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.clients.api.serializers import (
    ClientCreateSerializer,
    ClientDetailSerializer,
    ClientListSerializer,
    ClientUpdateSerializer,
)
from apps.clients.models import Client
from apps.clients.services import create_client, update_client
from apps.core.permissions import IsAdmin


class ClientViewSet(viewsets.ViewSet):
    """
    POST   /api/clients/       — create (admin only)
    GET    /api/clients/       — list (admin only)
    GET    /api/clients/{id}/  — detail (admin only)
    PATCH  /api/clients/{id}/  — update (admin only)
    """

    permission_classes = [IsAdmin]

    def _get_client(self, pk):
        try:
            return Client.objects.get(pk=pk)
        except (Client.DoesNotExist, ValueError):
            return None

    def list(self, request):
        qs = Client.objects.all()

        search = request.query_params.get("search", "").strip()
        if search:
            from django.db.models import Q

            qs = qs.filter(
                Q(company_name__icontains=search)
                | Q(contact_name__icontains=search)
            )

        status_filter = request.query_params.get("status", "").strip()
        if status_filter == "active":
            qs = qs.filter(is_active=True)
        elif status_filter == "inactive":
            qs = qs.filter(is_active=False)

        serializer = ClientListSerializer(qs, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ClientCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            client = create_client(
                actor=request.user,
                **serializer.validated_data,
            )
        except ValidationError as e:
            return Response(
                {"detail": e.messages if hasattr(e, "messages") else str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            ClientDetailSerializer(client).data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, pk=None):
        client = self._get_client(pk)
        if not client:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(ClientDetailSerializer(client).data)

    def partial_update(self, request, pk=None):
        client = self._get_client(pk)
        if not client:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ClientUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            client = update_client(
                client=client,
                actor=request.user,
                **serializer.validated_data,
            )
        except ValidationError as e:
            return Response(
                {"detail": e.messages if hasattr(e, "messages") else str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(ClientDetailSerializer(client).data)
