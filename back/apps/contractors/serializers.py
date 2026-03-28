from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Contractor

User = get_user_model()


class ContractorUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role"]
        read_only_fields = fields


class ContractorReadSerializer(serializers.ModelSerializer):
    user = ContractorUserSerializer(read_only=True)

    class Meta:
        model = Contractor
        fields = [
            "id", "user", "hourly_rate_default", "phone",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = fields


class ContractorCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=False, default="")
    last_name = serializers.CharField(required=False, default="")
    hourly_rate_default = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True, default=None
    )
    phone = serializers.CharField(required=False, default="")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            role=User.Role.CONTRACTOR,
        )
        contractor = Contractor.objects.create(
            user=user,
            hourly_rate_default=validated_data.get("hourly_rate_default"),
            phone=validated_data.get("phone", ""),
            created_by=self.context["request"].user,
            updated_by=self.context["request"].user,
        )
        return contractor


class ContractorUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)

    class Meta:
        model = Contractor
        fields = ["hourly_rate_default", "phone", "is_active", "first_name", "last_name"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.updated_by = self.context["request"].user
        instance.save()
        return instance
