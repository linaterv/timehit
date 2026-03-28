"""DRF serializers for Contractor management (S004)."""
from rest_framework import serializers

from apps.contractors.models import Contractor
from apps.users.models import User


class ContractorListSerializer(serializers.ModelSerializer):
    """Read-only list view of contractors."""

    email = serializers.EmailField(source="user.email")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    phone = serializers.CharField(source="user.phone")
    is_active = serializers.BooleanField(source="user.is_active")

    class Meta:
        model = Contractor
        fields = [
            "id", "email", "first_name", "last_name", "phone",
            "company_name", "is_active", "created_at",
        ]
        read_only_fields = fields


class ContractorDetailSerializer(serializers.ModelSerializer):
    """Full detail for a single contractor."""

    email = serializers.EmailField(source="user.email")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    phone = serializers.CharField(source="user.phone")
    is_active = serializers.BooleanField(source="user.is_active")
    user_id = serializers.UUIDField(source="user.id")

    class Meta:
        model = Contractor
        fields = [
            "id", "user_id", "email", "first_name", "last_name", "phone",
            "company_name", "tax_id", "bank_name", "bank_account",
            "address", "notes", "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = fields


class ContractorOwnProfileSerializer(serializers.ModelSerializer):
    """What the contractor sees about themselves (no notes)."""

    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = Contractor
        fields = [
            "id", "email", "first_name", "last_name", "phone",
            "company_name", "tax_id", "bank_name", "bank_account",
            "address",
        ]
        read_only_fields = ["id", "email", "first_name", "last_name"]


class ContractorCreateSerializer(serializers.Serializer):
    """Input for creating a contractor (user + profile in one step)."""

    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=30, required=False, default="")
    company_name = serializers.CharField(max_length=255, required=False, default="")
    tax_id = serializers.CharField(max_length=50, required=False, default="")
    bank_name = serializers.CharField(max_length=255, required=False, default="")
    bank_account = serializers.CharField(max_length=100)
    address = serializers.CharField(required=False, default="")
    notes = serializers.CharField(required=False, default="")

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class ContractorUpdateSerializer(serializers.Serializer):
    """Input for updating a contractor."""

    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    phone = serializers.CharField(max_length=30, required=False)
    company_name = serializers.CharField(max_length=255, required=False)
    tax_id = serializers.CharField(max_length=50, required=False)
    bank_name = serializers.CharField(max_length=255, required=False)
    bank_account = serializers.CharField(max_length=100, required=False)
    address = serializers.CharField(required=False)
    notes = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)


class ContractorSelfUpdateSerializer(serializers.Serializer):
    """Fields a contractor can edit on their own profile."""

    phone = serializers.CharField(max_length=30, required=False)
    bank_name = serializers.CharField(max_length=255, required=False)
    bank_account = serializers.CharField(max_length=100, required=False)
    address = serializers.CharField(required=False)
