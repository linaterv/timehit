"""DRF serializers for User management (S003)."""
from rest_framework import serializers

from apps.users.models import User, UserRole


class UserListSerializer(serializers.ModelSerializer):
    """Read-only serializer for user lists."""

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name",
            "role", "phone", "is_active", "created_at",
        ]
        read_only_fields = fields


class UserCreateSerializer(serializers.Serializer):
    """Serializer for creating agency users (admin/clerk)."""

    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    role = serializers.ChoiceField(choices=[
        (UserRole.ADMIN, "Admin"),
        (UserRole.CLERK, "Clerk"),
    ])
    phone = serializers.CharField(max_length=30, required=False, default="")

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class UserUpdateSerializer(serializers.Serializer):
    """Serializer for updating agency users."""

    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    role = serializers.ChoiceField(
        choices=[
            (UserRole.ADMIN, "Admin"),
            (UserRole.CLERK, "Clerk"),
        ],
        required=False,
    )
    phone = serializers.CharField(max_length=30, required=False)
    is_active = serializers.BooleanField(required=False)


class UserDetailSerializer(serializers.ModelSerializer):
    """Full detail for a single user (read-only, no password)."""

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name",
            "role", "phone", "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = fields
