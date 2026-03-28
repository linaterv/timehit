"""Tests for Contract model (S007)."""
import uuid
from datetime import date
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.contracts.models import Contract, ContractType, ContractStatus, MAX_FILE_SIZE


class ContractModelTests(TestCase):
    """Tests for Contract model validation."""

    def _make_file(self, name="test.pdf", size=1024, content_type="application/pdf"):
        return SimpleUploadedFile(name, b"x" * size, content_type=content_type)

    def test_create_minimal_contract(self):
        contract = Contract(
            title="Test Agreement",
            contract_type=ContractType.SERVICE_AGREEMENT,
            document=self._make_file(),
            file_name="test.pdf",
            file_size=1024,
            signed_date=date(2026, 1, 15),
        )
        contract.full_clean()
        contract.save()
        self.assertIsNotNone(contract.pk)
        self.assertEqual(contract.status, ContractStatus.DRAFT)
        self.assertTrue(contract.is_active)

    def test_title_required(self):
        contract = Contract(
            title="",
            contract_type=ContractType.NDA,
            document=self._make_file(),
            file_name="test.pdf",
            file_size=1024,
            signed_date=date(2026, 1, 15),
        )
        with self.assertRaises(ValidationError) as ctx:
            contract.full_clean()
        self.assertIn("title", ctx.exception.message_dict)

    def test_signed_date_required(self):
        contract = Contract(
            title="Test",
            contract_type=ContractType.NDA,
            document=self._make_file(),
            file_name="test.pdf",
            file_size=1024,
            signed_date=None,
        )
        with self.assertRaises(ValidationError):
            contract.full_clean()

    def test_invalid_file_extension(self):
        contract = Contract(
            title="Test",
            contract_type=ContractType.NDA,
            document=self._make_file(name="test.exe"),
            file_name="test.exe",
            file_size=1024,
            signed_date=date(2026, 1, 15),
        )
        with self.assertRaises(ValidationError) as ctx:
            contract.full_clean()
        self.assertIn("document", ctx.exception.message_dict)

    def test_file_too_large(self):
        big_file = self._make_file(size=MAX_FILE_SIZE + 1)
        contract = Contract(
            title="Test",
            contract_type=ContractType.NDA,
            document=big_file,
            file_name="big.pdf",
            file_size=MAX_FILE_SIZE + 1,
            signed_date=date(2026, 1, 15),
        )
        with self.assertRaises(ValidationError) as ctx:
            contract.full_clean()
        self.assertIn("document", ctx.exception.message_dict)

    def test_str(self):
        contract = Contract(
            title="Service Agreement",
            contract_type=ContractType.SERVICE_AGREEMENT,
        )
        self.assertEqual(str(contract), "Service Agreement (Service Agreement)")

    def test_uuid_primary_key(self):
        contract = Contract(
            title="UUID Test",
            contract_type=ContractType.OTHER,
            document=self._make_file(),
            file_name="test.pdf",
            file_size=1024,
            signed_date=date(2026, 3, 1),
        )
        contract.full_clean()
        contract.save()
        self.assertIsInstance(contract.pk, uuid.UUID)
