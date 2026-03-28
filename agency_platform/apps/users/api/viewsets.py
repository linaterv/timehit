"""DRF viewsets for User management (S003)."""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsAdmin
from apps.users.api.serializers import (
    UserCreateSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserUpdateSerializer,
)
from apps.users.models import User, UserRole
from apps.users.services import create_user, reset_user_password, update_user


class UserViewSet(viewsets.ViewSet):
    """
    Admin-only user management.
    POST   /api/users/          — create
    GET    /api/users/          — list
    GET    /api/users/{id}/     — detail
    PATCH  /api/users/{id}/     — update
    POST   /api/users/{id}/reset-password/ — reset password
    No DELETE — deactivate instead.
    """

    permission_classes = [IsAdmin]

    def list(self, request):
        qs = User.objects.filter(role__in=[UserRole.ADMIN, UserRole.CLERK])

        # Filter by role
        role = request.query_params.get("role")
        if role in (UserRole.ADMIN, UserRole.CLERK):
            qs = qs.filter(role=role)

        # Search by name or email
        search = request.query_params.get("search", "").strip()
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        serializer = UserListSerializer(qs, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, plain_password = create_user(
            actor=request.user,
            **serializer.validated_data,
        )

        data = UserDetailSerializer(user).data
        data["generated_password"] = plain_password
        return Response(data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except (User.DoesNotExist, ValueError):
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserDetailSerializer(user)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except (User.DoesNotExist, ValueError):
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from django.core.exceptions import ValidationError
        try:
            user = update_user(
                user=user,
                actor=request.user,
                **serializer.validated_data,
            )
        except ValidationError as e:
            return Response({"detail": str(e.message)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(UserDetailSerializer(user).data)

    @action(detail=True, methods=["post"], url_path="reset-password")
    def reset_password(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except (User.DoesNotExist, ValueError):
            return Response(status=status.HTTP_404_NOT_FOUND)

        new_password = reset_user_password(user=user, actor=request.user)
        return Response({"generated_password": new_password})
