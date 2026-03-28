"""E2E tests for the login flow."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


class TestLoginPage:
    """Tests for the login page rendering."""

    def test_login_page_loads(self, page: Page):
        """Login page renders with email, password, and submit button."""
        page.goto("/login")
        expect(page.get_by_test_id("email-input")).to_be_visible()
        expect(page.get_by_test_id("password-input")).to_be_visible()
        expect(page.get_by_test_id("login-button")).to_be_visible()

    def test_login_page_has_correct_input_types(self, page: Page):
        """Email input is type=email, password input is type=password."""
        page.goto("/login")
        expect(page.get_by_test_id("email-input")).to_have_attribute("type", "email")
        expect(page.get_by_test_id("password-input")).to_have_attribute("type", "password")


class TestLoginFlow:
    """Tests for the login submission flow."""

    def test_valid_login_redirects_to_dashboard(self, page: Page):
        """Valid credentials redirect to /dashboard."""
        page.goto("/login")
        page.get_by_test_id("email-input").fill("admin@timehit.local")
        page.get_by_test_id("password-input").fill("admin")
        page.get_by_test_id("login-button").click()

        page.wait_for_url("**/dashboard**", timeout=5000)

    def test_invalid_login_shows_error(self, page: Page):
        """Invalid credentials show an error message."""
        page.goto("/login")
        page.get_by_test_id("email-input").fill("admin@timehit.local")
        page.get_by_test_id("password-input").fill("wrongpassword")
        page.get_by_test_id("login-button").click()

        error = page.get_by_test_id("login-error")
        expect(error).to_be_visible(timeout=5000)
        expect(error).to_contain_text("Invalid")

    def test_empty_fields_shows_validation(self, page: Page):
        """Submitting with empty fields triggers HTML5 validation (required attributes)."""
        page.goto("/login")
        page.get_by_test_id("email-input").wait_for(state="visible", timeout=10000)

        # Both inputs have required attribute — browser blocks submission
        email_input = page.get_by_test_id("email-input")
        expect(email_input).to_have_attribute("required", "")

        # Click submit without filling — page should stay on /login
        page.get_by_test_id("login-button").click()
        page.wait_for_timeout(500)
        expect(page).to_have_url("/login")
