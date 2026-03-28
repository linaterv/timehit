"""Tests for contractor services (S004)."""
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.audit.models import AuditLog
from apps.contractors.models import Contractor
from apps.contractors.services import create_contractor, update_contractor
from apps.users.models import User, UserRole


class CreateContractorTests(TestCase):
    """Tests for create_contractor service."""

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            role=UserRole.ADMIN,
            first_name="Admin",
            last_name="User",
        )

    def test_create_contractor_success(self):
        contractor, password = create_contractor(
            email="john@example.com",
            first_name="John",
            last_name="Doe",
            bank_account="LT123456789",
            actor=self.admin,
        )
        self.assertIsInstance(contractor, Contractor)
        self.assertEqual(contractor.user.email, "john@example.com")
        self.assertEqual(contractor.user.role, UserRole.CONTRACTOR)
        self.assertEqual(contractor.bank_account, "LT123456789")
        self.assertTrue(len(password) >= 8)
        # User can authenticate with generated password
        self.assertTrue(contractor.user.check_password(password))

    def test_create_contractor_with_all_fields(self):
        contractor, _ = create_contractor(
            email="jane@example.com",
            first_name="Jane",
            last_name="Smith",
            phone="+370612345",
            company_name="Jane Corp",
            tax_id="LT999",
            bank_name="SEB",
            bank_account="LT987654321",
            address="123 Main St",
            notes="Internal note",
            actor=self.admin,
        )
        self.assertEqual(contractor.company_name, "Jane Corp")
        self.assertEqual(contractor.tax_id, "LT999")
        self.assertEqual(contractor.bank_name, "SEB")
        self.assertEqual(contractor.address, "123 Main St")
        self.assertEqual(contractor.notes, "Internal note")
        self.assertEqual(contractor.user.phone, "+370612345")

    def test_create_contractor_duplicate_email_fails(self):
        create_contractor(
            email="dup@example.com",
            first_name="First",
            last_name="User",
            bank_account="LT111",
            actor=self.admin,
        )
        with self.assertRaises(ValidationError):
            create_contractor(
                email="dup@example.com",
                first_name="Second",
                last_name="User",
                bank_account="LT222",
                actor=self.admin,
            )

    def test_create_contractor_empty_email_fails(self):
        with self.assertRaises(ValidationError):
            create_contractor(
                email="",
                first_name="No",
                last_name="Email",
                bank_account="LT333",
                actor=self.admin,
            )

    def test_create_contractor_audit_log(self):
        contractor, _ = create_contractor(
            email="audit@example.com",
            first_name="Audit",
            last_name="Test",
            bank_account="LT444",
            actor=self.admin,
        )
        log = AuditLog.objects.filter(
            action="contractor_created",
            target_type="contractor",
            target_id=contractor.pk,
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.detail["email"], "audit@example.com")


class UpdateContractorTests(TestCase):
    """Tests for update_contractor service."""

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            role=UserRole.ADMIN,
            first_name="Admin",
            last_name="User",
        )
        self.contractor, _ = create_contractor(
            email="contractor@test.com",
            first_name="Con",
            last_name="Tractor",
            bank_account="LT000",
            actor=self.admin,
        )

    def test_update_user_fields(self):
        update_contractor(
            contractor=self.contractor,
            actor=self.admin,
            first_name="Updated",
            last_name="Name",
            phone="+370999",
        )
        self.contractor.user.refresh_from_db()
        self.assertEqual(self.contractor.user.first_name, "Updated")
        self.assertEqual(self.contractor.user.last_name, "Name")
        self.assertEqual(self.contractor.user.phone, "+370999")

    def test_update_contractor_fields(self):
        update_contractor(
            contractor=self.contractor,
            actor=self.admin,
            company_name="New Corp",
            tax_id="LT888",
            address="456 Oak Ave",
            notes="Updated notes",
        )
        self.contractor.refresh_from_db()
        self.assertEqual(self.contractor.company_name, "New Corp")
        self.assertEqual(self.contractor.tax_id, "LT888")
        self.assertEqual(self.contractor.address, "456 Oak Ave")
        self.assertEqual(self.contractor.notes, "Updated notes")

    def test_update_bank_details_audit(self):
        update_contractor(
            contractor=self.contractor,
            actor=self.admin,
            bank_account="LT_NEW_ACCOUNT",
        )
        log = AuditLog.objects.filter(
            action="contractor_bank_details_changed",
            target_type="contractor",
            target_id=self.contractor.pk,
        ).first()
        self.assertIsNotNone(log)
        # Bank details should be masked in audit (shows last 4 chars)
        old_masked = log.detail["changes"]["bank_account"]["old"]
        self.assertIn("*", old_masked)
        self.assertNotEqual(old_masked, "LT000")  # not the raw value

    def test_deactivate_contractor(self):
        update_contractor(
            contractor=self.contractor,
            actor=self.admin,
            is_active=False,
        )
        self.contractor.user.refresh_from_db()
        self.assertFalse(self.contractor.user.is_active)
        log = AuditLog.objects.filter(
            action="contractor_deactivated",
        ).first()
        self.assertIsNotNone(log)

    def test_no_changes_no_audit(self):
        initial_count = AuditLog.objects.count()
        update_contractor(
            contractor=self.contractor,
            actor=self.admin,
            first_name=self.contractor.user.first_name,  # same value
        )
        self.assertEqual(AuditLog.objects.count(), initial_count)
