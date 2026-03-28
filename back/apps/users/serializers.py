from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "role": self.user.role,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
        }
        return data


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "role", "first_name", "last_name", "is_active", "date_joined"]
        read_only_fields = fields


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "email", "password", "role", "first_name", "last_name"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "role", "first_name", "last_name", "is_active"]


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "role", "first_name", "last_name"]
        read_only_fields = fields


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
