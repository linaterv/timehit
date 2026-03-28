"""DRF serializers for Client management (S005)."""
from rest_framework import serializers

from apps.clients.models import Client


class ClientListSerializer(serializers.ModelSerializer):
    """Read-only list view of clients."""

    class Meta:
        model = Client
        fields = [
            "id",
            "company_name",
            "contact_name",
            "contact_email",
            "is_active",
            "created_at",
        ]
        read_only_fields = fields


class ClientDetailSerializer(serializers.ModelSerializer):
    """Full detail for a single client."""

    class Meta:
        model = Client
        fields = [
            "id",
            "company_name",
            "billing_address",
            "tax_id",
            "contact_name",
            "contact_email",
            "contact_phone",
            "payment_terms",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
            "created_by",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
        ]


class ClientCreateSerializer(serializers.Serializer):
    """Input for creating a client."""

    company_name = serializers.CharField(max_length=255)
    billing_address = serializers.CharField()
    tax_id = serializers.CharField(max_length=50, required=False, default="")
    contact_name = serializers.CharField(max_length=255, required=False, default="")
    contact_email = serializers.EmailField(required=False, default="")
    contact_phone = serializers.CharField(max_length=30, required=False, default="")
    payment_terms = serializers.IntegerField(required=False, default=30, min_value=0)
    notes = serializers.CharField(required=False, default="")


class ClientUpdateSerializer(serializers.Serializer):
    """Input for updating a client (PATCH)."""

    company_name = serializers.CharField(max_length=255, required=False)
    billing_address = serializers.CharField(required=False)
    tax_id = serializers.CharField(max_length=50, required=False)
    contact_name = serializers.CharField(max_length=255, required=False)
    contact_email = serializers.EmailField(required=False)
    contact_phone = serializers.CharField(max_length=30, required=False)
    payment_terms = serializers.IntegerField(required=False, min_value=0)
    notes = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)
