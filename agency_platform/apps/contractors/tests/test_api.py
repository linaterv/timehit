"""Tests for contractor API (S004)."""
from django.test import TestCase
from rest_framework.test import APIClient

from apps.contractors.models import Contractor
from apps.contractors.services import create_contractor
from apps.users.models import User, UserRole


class ContractorAPITests(TestCase):
    """Tests for ContractorViewSet."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            role=UserRole.ADMIN,
            first_name="Admin",
            last_name="User",
        )
        self.contractor_user = User.objects.create_user(
            email="contractor@test.com",
            password="testpass123",
            role=UserRole.CONTRACTOR,
            first_name="Con",
            last_name="Tractor",
        )

    def _create_contractor(self, **kwargs):
        defaults = {
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "Contractor",
            "bank_account": "LT123",
            "actor": self.admin,
        }
        defaults.update(kwargs)
        return create_contractor(**defaults)

    # --- List ---

    def test_list_as_admin(self):
        self._create_contractor()
        self.client.force_authenticate(self.admin)
        resp = self.client.get("/api/contractors/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_list_as_contractor_sees_only_own(self):
        # Create a contractor profile for the contractor user
        contractor = Contractor.objects.create(
            user=self.contractor_user,
            bank_account="LT999",
        )
        self._create_contractor()  # another contractor
        self.client.force_authenticate(self.contractor_user)
        resp = self.client.get("/api/contractors/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["email"], "contractor@test.com")

    def test_list_unauthenticated(self):
        resp = self.client.get("/api/contractors/")
        self.assertIn(resp.status_code, [401, 403])

    # --- Create ---

    def test_create_as_admin(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post("/api/contractors/", {
            "email": "api-new@example.com",
            "first_name": "API",
            "last_name": "New",
            "bank_account": "LT555",
        })
        self.assertEqual(resp.status_code, 201)
        self.assertIn("generated_password", resp.data)
        self.assertEqual(resp.data["email"], "api-new@example.com")

    def test_create_as_contractor_forbidden(self):
        self.client.force_authenticate(self.contractor_user)
        resp = self.client.post("/api/contractors/", {
            "email": "sneaky@example.com",
            "first_name": "Sneaky",
            "last_name": "Try",
            "bank_account": "LT666",
        })
        self.assertEqual(resp.status_code, 403)

    def test_create_duplicate_email(self):
        self._create_contractor(email="dup@example.com")
        self.client.force_authenticate(self.admin)
        resp = self.client.post("/api/contractors/", {
            "email": "dup@example.com",
            "first_name": "Dup",
            "last_name": "Test",
            "bank_account": "LT777",
        })
        self.assertEqual(resp.status_code, 400)

    # --- Retrieve ---

    def test_retrieve_as_admin(self):
        contractor, _ = self._create_contractor()
        self.client.force_authenticate(self.admin)
        resp = self.client.get(f"/api/contractors/{contractor.pk}/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("notes", resp.data)  # admin sees full detail

    def test_retrieve_own_as_contractor(self):
        contractor = Contractor.objects.create(
            user=self.contractor_user,
            bank_account="LT999",
        )
        self.client.force_authenticate(self.contractor_user)
        resp = self.client.get(f"/api/contractors/{contractor.pk}/")
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("notes", resp.data)  # contractor doesn't see notes

    def test_retrieve_other_as_contractor_forbidden(self):
        contractor, _ = self._create_contractor()
        self.client.force_authenticate(self.contractor_user)
        resp = self.client.get(f"/api/contractors/{contractor.pk}/")
        self.assertEqual(resp.status_code, 403)

    # --- Update ---

    def test_partial_update_as_admin(self):
        contractor, _ = self._create_contractor()
        self.client.force_authenticate(self.admin)
        resp = self.client.patch(f"/api/contractors/{contractor.pk}/", {
            "company_name": "Updated Corp",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["company_name"], "Updated Corp")

    def test_self_update_limited_fields(self):
        contractor = Contractor.objects.create(
            user=self.contractor_user,
            bank_account="LT999",
        )
        self.client.force_authenticate(self.contractor_user)
        resp = self.client.patch(f"/api/contractors/{contractor.pk}/", {
            "phone": "+370555",
            "bank_account": "LT_UPDATED",
        })
        self.assertEqual(resp.status_code, 200)

    # --- Search ---

    def test_search_filter(self):
        self._create_contractor(email="findme@example.com", first_name="Findable")
        self._create_contractor(email="hidden@example.com", first_name="Hidden", last_name="One")
        self.client.force_authenticate(self.admin)
        resp = self.client.get("/api/contractors/?search=findme")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["email"], "findme@example.com")
