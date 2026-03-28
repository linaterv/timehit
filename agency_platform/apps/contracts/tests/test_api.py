"""Tests for Contract API (S007)."""
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from apps.clients.models import Client
from apps.contracts.models import Contract
from apps.contracts.services import create_contract
from apps.contractors.models import Contractor
from apps.users.models import User, UserRole


class ContractAPITests(TestCase):
    """Tests for ContractViewSet — per role."""

    def setUp(self):
        self.api = APIClient()
        self.admin = User.objects.create_user(
            email="admin@test.com", password="testpass123",
            role=UserRole.ADMIN, first_name="Admin", last_name="User",
        )
        self.clerk = User.objects.create_user(
            email="clerk@test.com", password="testpass123",
            role=UserRole.CLERK, first_name="Clerk", last_name="User",
        )
        self.con_user = User.objects.create_user(
            email="con@test.com", password="testpass123",
            role=UserRole.CONTRACTOR, first_name="Con", last_name="Tractor",
        )
        self.contractor = Contractor.objects.create(
            user=self.con_user, bank_account="LT123",
        )
        self.con_user2 = User.objects.create_user(
            email="con2@test.com", password="testpass123",
            role=UserRole.CONTRACTOR, first_name="Other", last_name="Con",
        )
        self.contractor2 = Contractor.objects.create(
            user=self.con_user2, bank_account="LT456",
        )
        self.client_co = Client.objects.create(
            company_name="Acme", billing_address="123 St",
        )

    def _make_file(self, name="test.pdf"):
        return SimpleUploadedFile(name, b"%PDF-1.4 test content", content_type="application/pdf")

    def _create_contract(self, contractor=None, client=None, title="Test Contract"):
        return create_contract(
            title=title,
            contract_type="nda",
            document=self._make_file(),
            signed_date=date(2026, 1, 15),
            contractor=contractor,
            client=client,
            actor=self.admin,
        )

    # --- Create ---

    def test_create_as_admin(self):
        self.api.force_authenticate(self.admin)
        resp = self.api.post("/api/contracts/", {
            "title": "New NDA",
            "contract_type": "nda",
            "document": self._make_file(),
            "signed_date": "2026-03-01",
        }, format="multipart")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["title"], "New NDA")

    def test_create_as_contractor_forbidden(self):
        self.api.force_authenticate(self.con_user)
        resp = self.api.post("/api/contracts/", {
            "title": "Sneaky",
            "contract_type": "nda",
            "document": self._make_file(),
            "signed_date": "2026-03-01",
        }, format="multipart")
        self.assertEqual(resp.status_code, 403)

    def test_create_as_clerk_forbidden(self):
        self.api.force_authenticate(self.clerk)
        resp = self.api.post("/api/contracts/", {
            "title": "Sneaky",
            "contract_type": "nda",
            "document": self._make_file(),
            "signed_date": "2026-03-01",
        }, format="multipart")
        self.assertEqual(resp.status_code, 403)

    def test_create_invalid_file_type(self):
        self.api.force_authenticate(self.admin)
        bad_file = SimpleUploadedFile("virus.exe", b"bad", content_type="application/octet-stream")
        resp = self.api.post("/api/contracts/", {
            "title": "Bad File",
            "contract_type": "other",
            "document": bad_file,
            "signed_date": "2026-03-01",
        }, format="multipart")
        self.assertEqual(resp.status_code, 400)

    # --- List ---

    def test_list_as_admin(self):
        self._create_contract(contractor=self.contractor)
        self._create_contract(contractor=self.contractor2, title="Other")
        self.api.force_authenticate(self.admin)
        resp = self.api.get("/api/contracts/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)

    def test_list_as_contractor_sees_own_only(self):
        self._create_contract(contractor=self.contractor)
        self._create_contract(contractor=self.contractor2, title="Other's")
        self.api.force_authenticate(self.con_user)
        resp = self.api.get("/api/contracts/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["title"], "Test Contract")

    def test_list_as_clerk_sees_all(self):
        self._create_contract(contractor=self.contractor)
        self.api.force_authenticate(self.clerk)
        resp = self.api.get("/api/contracts/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_list_unauthenticated(self):
        resp = self.api.get("/api/contracts/")
        self.assertIn(resp.status_code, [401, 403])

    # --- Retrieve ---

    def test_retrieve_as_admin(self):
        contract = self._create_contract(contractor=self.contractor)
        self.api.force_authenticate(self.admin)
        resp = self.api.get(f"/api/contracts/{contract.pk}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["title"], "Test Contract")

    def test_retrieve_own_as_contractor(self):
        contract = self._create_contract(contractor=self.contractor)
        self.api.force_authenticate(self.con_user)
        resp = self.api.get(f"/api/contracts/{contract.pk}/")
        self.assertEqual(resp.status_code, 200)

    def test_retrieve_other_as_contractor_forbidden(self):
        contract = self._create_contract(contractor=self.contractor2)
        self.api.force_authenticate(self.con_user)
        resp = self.api.get(f"/api/contracts/{contract.pk}/")
        self.assertEqual(resp.status_code, 403)

    # --- Update ---

    def test_update_as_admin(self):
        contract = self._create_contract()
        self.api.force_authenticate(self.admin)
        resp = self.api.patch(f"/api/contracts/{contract.pk}/", {
            "title": "Updated Title",
            "status": "active",
        }, format="multipart")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["title"], "Updated Title")

    def test_update_as_contractor_forbidden(self):
        contract = self._create_contract(contractor=self.contractor)
        self.api.force_authenticate(self.con_user)
        resp = self.api.patch(f"/api/contracts/{contract.pk}/", {
            "title": "Hacked",
        }, format="multipart")
        self.assertEqual(resp.status_code, 403)

    def test_update_replace_file(self):
        contract = self._create_contract()
        self.api.force_authenticate(self.admin)
        new_file = SimpleUploadedFile("replacement.pdf", b"%PDF new", content_type="application/pdf")
        resp = self.api.patch(f"/api/contracts/{contract.pk}/", {
            "document": new_file,
        }, format="multipart")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["file_name"], "replacement.pdf")

    # --- Download ---

    def test_download_as_admin(self):
        contract = self._create_contract()
        self.api.force_authenticate(self.admin)
        resp = self.api.get(f"/api/contracts/{contract.pk}/download/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("attachment", resp.get("Content-Disposition", ""))

    def test_download_own_as_contractor(self):
        contract = self._create_contract(contractor=self.contractor)
        self.api.force_authenticate(self.con_user)
        resp = self.api.get(f"/api/contracts/{contract.pk}/download/")
        self.assertEqual(resp.status_code, 200)

    def test_download_other_as_contractor_forbidden(self):
        contract = self._create_contract(contractor=self.contractor2)
        self.api.force_authenticate(self.con_user)
        resp = self.api.get(f"/api/contracts/{contract.pk}/download/")
        self.assertEqual(resp.status_code, 403)

    # --- Filters ---

    def test_filter_by_type(self):
        self._create_contract()
        self.api.force_authenticate(self.admin)
        resp = self.api.get("/api/contracts/?contract_type=nda")
        self.assertEqual(len(resp.data), 1)
        resp2 = self.api.get("/api/contracts/?contract_type=amendment")
        self.assertEqual(len(resp2.data), 0)

    def test_filter_by_status(self):
        self._create_contract()
        self.api.force_authenticate(self.admin)
        resp = self.api.get("/api/contracts/?status=draft")
        self.assertEqual(len(resp.data), 1)
        resp2 = self.api.get("/api/contracts/?status=active")
        self.assertEqual(len(resp2.data), 0)

    def test_search(self):
        self._create_contract(title="Special NDA")
        self._create_contract(title="Service Agreement")
        self.api.force_authenticate(self.admin)
        resp = self.api.get("/api/contracts/?search=Special")
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["title"], "Special NDA")
