from rest_framework import serializers

from .models import Placement


class PlacementReadSerializer(serializers.ModelSerializer):
    contractor_name = serializers.CharField(source="contractor.user.get_full_name", read_only=True)
    contractor_email = serializers.EmailField(source="contractor.user.email", read_only=True)
    client_name = serializers.CharField(source="client.name", read_only=True)
    margin = serializers.SerializerMethodField()

    class Meta:
        model = Placement
        fields = [
            "id", "contractor", "contractor_name", "contractor_email",
            "client", "client_name", "client_rate", "contractor_rate",
            "margin", "start_date", "end_date", "approval_mode",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = fields

    def get_margin(self, obj):
        return str(obj.margin)


class PlacementWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Placement
        fields = [
            "contractor", "client", "client_rate", "contractor_rate",
            "start_date", "end_date", "approval_mode", "is_active",
        ]
