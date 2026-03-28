"""DRF serializers for Contract management (S007)."""
from rest_framework import serializers

from apps.contracts.models import Contract, ContractType, ContractStatus, ALLOWED_EXTENSIONS, MAX_FILE_SIZE


class ContractListSerializer(serializers.ModelSerializer):
    """Read-only list view of contracts."""

    contractor_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    contract_type_display = serializers.CharField(
        source="get_contract_type_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Contract
        fields = [
            "id", "title", "contract_type", "contract_type_display",
            "contractor_name", "client_name",
            "signed_date", "expiry_date", "status", "status_display",
            "file_name", "file_size", "created_at",
        ]
        read_only_fields = fields

    def get_contractor_name(self, obj):
        if obj.contractor:
            return obj.contractor.user.get_full_name()
        return None

    def get_client_name(self, obj):
        if obj.client:
            return obj.client.company_name
        return None


class ContractDetailSerializer(serializers.ModelSerializer):
    """Full detail for a single contract."""

    contractor_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    contract_type_display = serializers.CharField(
        source="get_contract_type_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            "id", "title", "contract_type", "contract_type_display",
            "contractor", "contractor_name",
            "client", "client_name",
            "placement_id",
            "signed_date", "expiry_date",
            "status", "status_display",
            "file_name", "file_size",
            "notes", "is_active",
            "download_url",
            "created_at", "updated_at",
            "created_by", "updated_by",
        ]
        read_only_fields = fields

    def get_contractor_name(self, obj):
        if obj.contractor:
            return obj.contractor.user.get_full_name()
        return None

    def get_client_name(self, obj):
        if obj.client:
            return obj.client.company_name
        return None

    def get_download_url(self, obj):
        return f"/api/contracts/{obj.pk}/download/"


class ContractCreateSerializer(serializers.Serializer):
    """Input for creating a contract with file upload."""

    title = serializers.CharField(max_length=255)
    contract_type = serializers.ChoiceField(
        choices=ContractType.choices, default=ContractType.OTHER
    )
    document = serializers.FileField()
    signed_date = serializers.DateField()
    expiry_date = serializers.DateField(required=False, allow_null=True)
    contractor = serializers.IntegerField(required=False, allow_null=True)
    client = serializers.UUIDField(required=False, allow_null=True)
    status = serializers.ChoiceField(
        choices=ContractStatus.choices, default=ContractStatus.DRAFT
    )
    notes = serializers.CharField(required=False, default="", allow_blank=True)

    def validate_document(self, value):
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"File type not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        if value.size > MAX_FILE_SIZE:
            raise serializers.ValidationError(
                f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)} MB."
            )
        return value


class ContractUpdateSerializer(serializers.Serializer):
    """Input for updating a contract."""

    title = serializers.CharField(max_length=255, required=False)
    contract_type = serializers.ChoiceField(
        choices=ContractType.choices, required=False
    )
    document = serializers.FileField(required=False)
    signed_date = serializers.DateField(required=False)
    expiry_date = serializers.DateField(required=False, allow_null=True)
    contractor = serializers.IntegerField(required=False, allow_null=True)
    client = serializers.UUIDField(required=False, allow_null=True)
    status = serializers.ChoiceField(
        choices=ContractStatus.choices, required=False
    )
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_document(self, value):
        if value:
            import os
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise serializers.ValidationError(
                    f"File type not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            if value.size > MAX_FILE_SIZE:
                raise serializers.ValidationError(
                    f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)} MB."
                )
        return value
