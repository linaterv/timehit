"""E2E tests for user management at /admin/users.

Important: tokens are stored in-memory by the frontend. After login, use
client-side navigation (sidebar clicks), NOT page.goto() to other pages.
"""

from __future__ import annotations

import uuid
import pytest
import httpx
from playwright.sync_api import Page, expect

API_BASE_URL = "http://192.168.0.115:8000"


class TestUserListPage:
    """Tests for the /admin/users page."""

    def test_users_page_shows_user_table(self, logged_in_admin):
        """Admin navigating to /admin/users sees the user table."""
        page = logged_in_admin
        page.get_by_test_id("sidebar-nav-admin-users").click()
        page.wait_for_url("**/admin/users**", timeout=5000)

        expect(page.get_by_test_id("user-table")).to_be_visible(timeout=10000)

    def test_users_page_has_create_button(self, logged_in_admin):
        """Admin sees a create-user button."""
        page = logged_in_admin
        page.get_by_test_id("sidebar-nav-admin-users").click()
        page.wait_for_url("**/admin/users**", timeout=5000)

        expect(page.get_by_test_id("create-user-button")).to_be_visible(timeout=10000)

    def test_users_page_has_role_filter(self, logged_in_admin):
        """Admin sees a role filter on the users page."""
        page = logged_in_admin
        page.get_by_test_id("sidebar-nav-admin-users").click()
        page.wait_for_url("**/admin/users**", timeout=5000)

        expect(page.get_by_test_id("role-filter")).to_be_visible(timeout=10000)


class TestCreateUser:
    """Tests for creating a user via the UI."""

    def test_create_user_dialog_opens(self, logged_in_admin):
        """Clicking create-user-button opens the create dialog."""
        page = logged_in_admin
        page.get_by_test_id("sidebar-nav-admin-users").click()
        page.wait_for_url("**/admin/users**", timeout=5000)
        expect(page.get_by_test_id("user-table")).to_be_visible(timeout=10000)

        page.get_by_test_id("create-user-button").click()
        expect(page.get_by_test_id("create-user-dialog")).to_be_visible(timeout=5000)

    def test_create_user_via_dialog(self, logged_in_admin, admin_api_token):
        """Admin creates a new user through the create dialog and it appears in the table."""
        page = logged_in_admin
        page.get_by_test_id("sidebar-nav-admin-users").click()
        page.wait_for_url("**/admin/users**", timeout=5000)
        expect(page.get_by_test_id("user-table")).to_be_visible(timeout=10000)

        email = f"e2e-create-{uuid.uuid4().hex[:8]}@timehit.local"

        # Open dialog
        page.get_by_test_id("create-user-button").click()
        dialog = page.get_by_test_id("create-user-dialog")
        expect(dialog).to_be_visible(timeout=5000)

        # Fill in user details using data-testid attributes
        dialog.get_by_test_id("user-firstname-input").fill("Created")
        dialog.get_by_test_id("user-lastname-input").fill("ByE2E")
        dialog.get_by_test_id("user-email-input").fill(email)
        dialog.get_by_test_id("user-password-input").fill("TestPass123!")

        # Select role
        dialog.get_by_test_id("user-role-select").click()
        page.get_by_role("option", name="CONTRACTOR").click()

        # Submit
        dialog.get_by_role("button", name="Create User").click()
        page.wait_for_timeout(2000)

        # Verify user appears in table
        table = page.get_by_test_id("user-table")
        expect(table).to_contain_text(email, timeout=5000)

        # Cleanup via API
        resp = httpx.get(
            f"{API_BASE_URL}/api/users/",
            headers={"Authorization": f"Bearer {admin_api_token}"},
        )
        users = resp.json()["results"]
        created = next((u for u in users if u["email"] == email), None)
        if created:
            httpx.delete(
                f"{API_BASE_URL}/api/users/{created['id']}/",
                headers={"Authorization": f"Bearer {admin_api_token}"},
            )


class TestEditUser:
    """Tests for editing a user via the UI."""

    def test_edit_user_name(self, logged_in_admin, created_e2e_user, admin_api_token):
        """Admin edits a user's first name via the edit dialog."""
        page = logged_in_admin
        page.get_by_test_id("sidebar-nav-admin-users").click()
        page.wait_for_url("**/admin/users**", timeout=5000)
        expect(page.get_by_test_id("user-table")).to_be_visible(timeout=10000)

        user_id = created_e2e_user["id"]

        # Find the user row and open actions
        row = page.get_by_test_id(f"user-row-{user_id}")
        expect(row).to_be_visible(timeout=5000)
        row.get_by_role("button", name="Actions").click()
        page.get_by_role("menuitem", name="Edit").click()
        page.wait_for_timeout(1000)

        # Edit first name
        firstname = page.get_by_test_id("user-firstname-input")
        firstname.clear()
        firstname.fill("Edited")

        # Save
        page.get_by_role("button", name="Save Changes").click()
        page.wait_for_timeout(2000)

        # Verify the table reflects the change
        expect(row).to_contain_text("Edited", timeout=5000)


class TestDeactivateUser:
    """Tests for deactivating a user via the UI."""

    @pytest.mark.xfail(
        reason="DEFECT: Deactivate button sends DELETE instead of PATCH {is_active: false}. "
        "User is permanently deleted instead of deactivated."
    )
    def test_deactivate_user(self, logged_in_admin, created_e2e_user, admin_api_token):
        """Admin deactivates a user from the actions dropdown.

        DEFECT: The frontend "Deactivate" button sends DELETE /api/users/{id}/
        (which permanently removes the user) instead of PATCH /api/users/{id}/
        with {is_active: false}. The user disappears from the table entirely
        rather than showing as Inactive. This is a data loss bug.
        """
        page = logged_in_admin
        page.get_by_test_id("sidebar-nav-admin-users").click()
        page.wait_for_url("**/admin/users**", timeout=5000)
        expect(page.get_by_test_id("user-table")).to_be_visible(timeout=10000)

        user_id = created_e2e_user["id"]

        # Find the user row and open actions
        row = page.get_by_test_id(f"user-row-{user_id}")
        expect(row).to_be_visible(timeout=5000)
        row.get_by_role("button", name="Actions").click()

        # Click deactivate in the dropdown
        page.get_by_test_id(f"deactivate-user-button-{user_id}").click()

        # Confirm in the confirmation dialog
        dialog = page.locator("[role='dialog']")
        expect(dialog).to_be_visible(timeout=5000)
        dialog.get_by_role("button", name="Deactivate").click()
        page.wait_for_timeout(2000)

        # Verify user shows as Inactive in the table (not deleted)
        expect(row).to_contain_text("Inactive", timeout=5000)
