"""Tests for contractor UI views (S004)."""
from django.test import TestCase, Client

from apps.contractors.models import Contractor
from apps.contractors.services import create_contractor
from apps.users.models import User, UserRole


class ContractorViewTests(TestCase):
    """Tests for contractor management views."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            role=UserRole.ADMIN,
            first_name="Admin",
            last_name="User",
        )
        self.client.login(email="admin@test.com", password="testpass123")

    def test_contractor_list(self):
        resp = self.client.get("/contractors/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Contractors")

    def test_contractor_create_get(self):
        resp = self.client.get("/contractors/create/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Create Contractor")

    def test_contractor_create_post(self):
        resp = self.client.post("/contractors/create/", {
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "Contractor",
            "bank_account": "LT123456",
        })
        self.assertEqual(resp.status_code, 302)  # redirect on success
        self.assertTrue(Contractor.objects.filter(user__email="new@example.com").exists())

    def test_contractor_edit_get(self):
        contractor, _ = create_contractor(
            email="edit@example.com",
            first_name="Edit",
            last_name="Me",
            bank_account="LT789",
            actor=self.admin,
        )
        resp = self.client.get(f"/contractors/{contractor.pk}/edit/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "edit@example.com")

    def test_contractor_edit_post(self):
        contractor, _ = create_contractor(
            email="edit2@example.com",
            first_name="Old",
            last_name="Name",
            bank_account="LT789",
            actor=self.admin,
        )
        resp = self.client.post(f"/contractors/{contractor.pk}/edit/", {
            "first_name": "Updated",
            "last_name": "Name",
            "bank_account": "LT789",
        })
        self.assertEqual(resp.status_code, 302)
        contractor.user.refresh_from_db()
        self.assertEqual(contractor.user.first_name, "Updated")

    def test_contractor_deactivate(self):
        contractor, _ = create_contractor(
            email="deact@example.com",
            first_name="Deact",
            last_name="Test",
            bank_account="LT000",
            actor=self.admin,
        )
        resp = self.client.post(f"/contractors/{contractor.pk}/deactivate/")
        self.assertEqual(resp.status_code, 302)
        contractor.user.refresh_from_db()
        self.assertFalse(contractor.user.is_active)

    def test_non_admin_forbidden(self):
        clerk = User.objects.create_user(
            email="clerk@test.com",
            password="testpass123",
            role=UserRole.CLERK,
        )
        self.client.login(email="clerk@test.com", password="testpass123")
        resp = self.client.get("/contractors/")
        self.assertEqual(resp.status_code, 403)

    def test_contractor_list_search(self):
        create_contractor(
            email="findme@example.com",
            first_name="Find",
            last_name="Me",
            bank_account="LT111",
            actor=self.admin,
        )
        create_contractor(
            email="other@example.com",
            first_name="Other",
            last_name="One",
            bank_account="LT222",
            actor=self.admin,
        )
        resp = self.client.get("/contractors/?search=findme")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "findme@example.com")
        self.assertNotContains(resp, "other@example.com")
