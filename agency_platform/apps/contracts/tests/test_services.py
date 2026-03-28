"""Tests for Contract services (S007)."""
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.audit.models import AuditLog
from apps.contracts.models import Contract, ContractType
from apps.contracts.services import create_contract, log_contract_download, update_contract
from apps.users.models import User, UserRole


class CreateContractTests(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            role=UserRole.ADMIN,
            first_name="Admin",
            last_name="User",
        )

    def _make_file(self, name="contract.pdf", size=2048):
        return SimpleUploadedFile(name, b"x" * size, content_type="application/pdf")

    def test_create_contract_success(self):
        contract = create_contract(
            title="Service Agreement",
            contract_type=ContractType.SERVICE_AGREEMENT,
            document=self._make_file(),
            signed_date=date(2026, 1, 15),
            actor=self.admin,
        )
        self.assertIsNotNone(contract.pk)
        self.assertEqual(contract.title, "Service Agreement")
        self.assertEqual(contract.file_name, "contract.pdf")
        self.assertEqual(contract.file_size, 2048)

        # Audit log
        log = AuditLog.objects.filter(action="contract_uploaded").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.detail["title"], "Service Agreement")

    def test_create_contract_with_links(self):
        from apps.clients.models import Client
        from apps.contractors.models import Contractor

        contractor_user = User.objects.create_user(
            email="con@test.com", password="testpass123",
            role=UserRole.CONTRACTOR, first_name="Con", last_name="Tractor",
        )
        contractor = Contractor.objects.create(user=contractor_user, bank_account="LT123")

        client = Client.objects.create(
            company_name="Acme Corp",
            billing_address="123 Main St",
        )

        contract = create_contract(
            title="NDA",
            contract_type=ContractType.NDA,
            document=self._make_file(),
            signed_date=date(2026, 2, 1),
            contractor=contractor,
            client=client,
            actor=self.admin,
        )
        self.assertEqual(contract.contractor, contractor)
        self.assertEqual(contract.client, client)


class UpdateContractTests(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            role=UserRole.ADMIN,
            first_name="Admin",
            last_name="User",
        )
        self.contract = create_contract(
            title="Original Title",
            contract_type=ContractType.OTHER,
            document=SimpleUploadedFile("orig.pdf", b"x" * 100, "application/pdf"),
            signed_date=date(2026, 1, 1),
            actor=self.admin,
        )

    def test_update_metadata(self):
        update_contract(
            contract=self.contract,
            actor=self.admin,
            title="Updated Title",
            status="active",
        )
        self.contract.refresh_from_db()
        self.assertEqual(self.contract.title, "Updated Title")
        self.assertEqual(self.contract.status, "active")

        log = AuditLog.objects.filter(action="contract_updated").first()
        self.assertIsNotNone(log)

    def test_replace_file(self):
        old_name = self.contract.file_name
        new_file = SimpleUploadedFile("new.pdf", b"y" * 200, "application/pdf")
        update_contract(
            contract=self.contract,
            actor=self.admin,
            new_document=new_file,
        )
        self.contract.refresh_from_db()
        self.assertEqual(self.contract.file_name, "new.pdf")
        self.assertEqual(self.contract.file_size, 200)

        log = AuditLog.objects.filter(action="contract_file_replaced").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.detail["changes"]["document"]["old_file"], old_name)

    def test_no_changes_no_audit(self):
        initial_count = AuditLog.objects.count()
        update_contract(
            contract=self.contract,
            actor=self.admin,
        )
        self.assertEqual(AuditLog.objects.count(), initial_count)


class DownloadAuditTests(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            role=UserRole.ADMIN,
            first_name="Admin",
            last_name="User",
        )
        self.contract = create_contract(
            title="Download Test",
            contract_type=ContractType.OTHER,
            document=SimpleUploadedFile("dl.pdf", b"x" * 100, "application/pdf"),
            signed_date=date(2026, 1, 1),
            actor=self.admin,
        )

    def test_download_logged(self):
        log_contract_download(contract=self.contract, actor=self.admin)
        log = AuditLog.objects.filter(action="contract_downloaded").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.detail["file_name"], "dl.pdf")
