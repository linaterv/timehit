import pytest
from django.db import IntegrityError

from apps.users.models import User, UserRole


@pytest.mark.django_db
class TestUserManager:
    def test_create_user(self):
        user = User.objects.create_user(
            email="dev@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            role=UserRole.CONTRACTOR,
        )
        assert user.email == "dev@example.com"
        assert user.role == UserRole.CONTRACTOR
        assert user.check_password("testpass123")
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_normalizes_email(self):
        user = User.objects.create_user(
            email="Dev@EXAMPLE.COM",
            password="testpass123",
            role=UserRole.CLERK,
            first_name="A",
            last_name="B",
        )
        assert user.email == "Dev@example.com"

    def test_create_user_without_email_raises(self):
        with pytest.raises(ValueError, match="Email is required"):
            User.objects.create_user(
                email="", password="testpass123", role=UserRole.ADMIN,
                first_name="A", last_name="B",
            )

    def test_create_user_without_role_raises(self):
        with pytest.raises(ValueError, match="Role is required"):
            User.objects.create_user(
                email="no-role@example.com", password="testpass123",
                first_name="A", last_name="B",
            )

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass",
            first_name="Super",
            last_name="Admin",
        )
        assert user.is_staff
        assert user.is_superuser
        assert user.role == UserRole.ADMIN

    def test_duplicate_email_raises(self):
        User.objects.create_user(
            email="dup@example.com", password="pass",
            role=UserRole.ADMIN, first_name="A", last_name="B",
        )
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="dup@example.com", password="pass",
                role=UserRole.CLERK, first_name="C", last_name="D",
            )


@pytest.mark.django_db
class TestUserModel:
    def test_uuid_pk(self):
        user = User.objects.create_user(
            email="uuid@example.com", password="pass",
            role=UserRole.ADMIN, first_name="A", last_name="B",
        )
        import uuid
        assert isinstance(user.pk, uuid.UUID)

    def test_str(self):
        user = User.objects.create_user(
            email="str@example.com", password="pass",
            role=UserRole.ADMIN, first_name="A", last_name="B",
        )
        assert str(user) == "str@example.com"

    def test_is_active_default_true(self):
        user = User.objects.create_user(
            email="active@example.com", password="pass",
            role=UserRole.ADMIN, first_name="A", last_name="B",
        )
        assert user.is_active is True

    def test_inactive_user_cannot_authenticate(self):
        from django.contrib.auth import authenticate
        User.objects.create_user(
            email="inactive@example.com", password="pass",
            role=UserRole.ADMIN, first_name="A", last_name="B",
            is_active=False,
        )
        assert authenticate(username="inactive@example.com", password="pass") is None
