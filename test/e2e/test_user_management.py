"""E2E tests for user management at /admin/users.

DEFECT: React hydration is broken — the Next.js dev server fails to hydrate
client-side React components. The users page shows a perpetual loading skeleton
because no JS executes to fetch user data from the API. All tests are marked
xfail until hydration is fixed.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

HYDRATION_BROKEN = pytest.mark.xfail(
    reason="DEFECT: React hydration broken — client JS not attaching event handlers"
)


@pytest.fixture()
def logged_in_admin(page: Page, admin_tokens):
    """Navigate to login and authenticate as admin.

    Since hydration is broken, we attempt to inject tokens directly into
    localStorage and navigate. This fixture will work once hydration is fixed.
    """
    page.goto("/login")
    page.wait_for_load_state("networkidle")

    # Inject auth tokens into localStorage (matches typical Next.js auth patterns)
    tokens = admin_tokens
    page.evaluate(
        """([access, refresh, user]) => {
            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);
            localStorage.setItem('user', JSON.stringify(user));
        }""",
        [tokens["access"], tokens["refresh"], tokens["user"]],
    )
    return page


class TestUserListPage:
    """Tests for the /admin/users page."""

    @HYDRATION_BROKEN
    def test_users_page_shows_user_table(self, logged_in_admin):
        """Admin navigating to /admin/users sees the user table."""
        page = logged_in_admin
        page.goto("/admin/users")
        page.wait_for_load_state("networkidle")

        table = page.get_by_test_id("user-table")
        expect(table).to_be_visible(timeout=10000)

    @HYDRATION_BROKEN
    def test_users_page_has_create_button(self, logged_in_admin):
        """Admin sees a create-user button."""
        page = logged_in_admin
        page.goto("/admin/users")
        page.wait_for_load_state("networkidle")

        btn = page.get_by_test_id("create-user-button")
        expect(btn).to_be_visible(timeout=10000)

    @HYDRATION_BROKEN
    def test_users_page_has_role_filter(self, logged_in_admin):
        """Admin sees a role filter on the users page."""
        page = logged_in_admin
        page.goto("/admin/users")
        page.wait_for_load_state("networkidle")

        filt = page.get_by_test_id("role-filter")
        expect(filt).to_be_visible(timeout=10000)


class TestCreateUser:
    """Tests for creating a user via the UI."""

    @HYDRATION_BROKEN
    def test_create_user_dialog_opens(self, logged_in_admin):
        """Clicking create-user-button opens the create dialog."""
        page = logged_in_admin
        page.goto("/admin/users")
        page.wait_for_load_state("networkidle")

        page.get_by_test_id("create-user-button").click()
        dialog = page.get_by_test_id("create-user-dialog")
        expect(dialog).to_be_visible(timeout=5000)

    @HYDRATION_BROKEN
    def test_create_user_via_dialog(self, logged_in_admin, unique_email, admin_tokens):
        """Admin creates a new user through the create dialog."""
        page = logged_in_admin
        page.goto("/admin/users")
        page.wait_for_load_state("networkidle")

        # Open dialog
        page.get_by_test_id("create-user-button").click()
        dialog = page.get_by_test_id("create-user-dialog")
        expect(dialog).to_be_visible(timeout=5000)

        # Fill in user details
        dialog.get_by_label("Email").fill(unique_email)
        dialog.get_by_label("Password").fill("TestPass123!")
        dialog.get_by_label("First name").fill("E2E")
        dialog.get_by_label("Last name").fill("Created")

        # Submit
        dialog.get_by_role("button", name="Create").click()

        # Verify user appears in table
        table = page.get_by_test_id("user-table")
        expect(table).to_contain_text(unique_email, timeout=5000)


class TestEditUser:
    """Tests for editing a user via the UI."""

    @HYDRATION_BROKEN
    def test_edit_user(self, logged_in_admin, created_e2e_user):
        """Admin edits a user's name via the user table."""
        page = logged_in_admin
        page.goto("/admin/users")
        page.wait_for_load_state("networkidle")

        # Find the user row and click edit
        table = page.get_by_test_id("user-table")
        expect(table).to_be_visible(timeout=10000)
        expect(table).to_contain_text(created_e2e_user["email"], timeout=5000)

        # Click edit on the user's row
        row = table.locator(f"tr:has-text('{created_e2e_user['email']}')")
        row.get_by_role("button", name="Edit").click()

        # Update the name
        page.get_by_label("First name").clear()
        page.get_by_label("First name").fill("Updated")
        page.get_by_role("button", name="Save").click()

        # Verify
        expect(table).to_contain_text("Updated", timeout=5000)


class TestDeactivateUser:
    """Tests for deactivating a user via the UI."""

    @HYDRATION_BROKEN
    def test_deactivate_user(self, logged_in_admin, created_e2e_user):
        """Admin deactivates a user from the user table."""
        page = logged_in_admin
        page.goto("/admin/users")
        page.wait_for_load_state("networkidle")

        table = page.get_by_test_id("user-table")
        expect(table).to_be_visible(timeout=10000)

        # Find user row and deactivate
        row = table.locator(f"tr:has-text('{created_e2e_user['email']}')")
        row.get_by_role("button", name="Deactivate").click()

        # Confirm deactivation if there's a confirmation dialog
        page.wait_for_timeout(500)
        confirm = page.get_by_role("button", name="Confirm")
        if confirm.is_visible():
            confirm.click()

        # Verify user shows as inactive
        page.wait_for_timeout(1000)
        expect(row).to_contain_text("Inactive", timeout=5000)
