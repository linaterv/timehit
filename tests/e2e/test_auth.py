"""E2E tests for authentication flows."""
import re

from playwright.sync_api import expect


def test_login_page_loads(page, base_url):
    """Login page renders with email/password fields and submit button."""
    page.goto(f"{base_url}/login/")
    expect(page.locator("h2")).to_have_text("Login")
    expect(page.locator("#email")).to_be_visible()
    expect(page.locator("#password")).to_be_visible()
    expect(page.locator("button[type='submit']")).to_have_text("Sign In")


def test_login_valid_credentials(page, base_url):
    """Logging in with valid creds redirects to the dashboard."""
    page.goto(f"{base_url}/login/")
    page.fill("#email", "a@a.a")
    page.fill("#password", "a")
    page.click("button[type='submit']")
    page.wait_for_url(re.compile(r".*/dashboard/"))
    expect(page.locator("h1")).to_have_text("Dashboard")


def test_login_wrong_password(page, base_url):
    """Wrong password stays on login page and shows an error."""
    page.goto(f"{base_url}/login/")
    page.fill("#email", "a@a.a")
    page.fill("#password", "wrong_password")
    page.click("button[type='submit']")
    # Should stay on login
    expect(page).to_have_url(re.compile(r".*/login/"))
    # Error message visible
    expect(page.locator(".alert, .messages, .errorlist, .alert-danger")).to_be_visible()


def test_logout_redirects_to_login(logged_in_page, base_url):
    """Logging out redirects back to login."""
    page = logged_in_page
    # Logout is a POST — find and submit the logout form
    # The base template should have a logout form/link
    # Let's navigate to dashboard first, then do a POST to /logout/
    page.goto(f"{base_url}/dashboard/")
    # Submit a POST to /logout/ via JS since it's POST-only
    page.evaluate("""() => {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/logout/';
        const csrf = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrf) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrfmiddlewaretoken';
            input.value = csrf.value;
            form.appendChild(input);
        }
        document.body.appendChild(form);
        form.submit();
    }""")
    page.wait_for_url(re.compile(r".*/login/"))
    expect(page.locator("h2")).to_have_text("Login")


def test_unauthenticated_access_redirects_to_login(page, base_url):
    """Accessing a protected page without login redirects to login."""
    page.goto(f"{base_url}/dashboard/")
    expect(page).to_have_url(re.compile(r".*/login/"))
