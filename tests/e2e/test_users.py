"""E2E tests for user management CRUD."""
import re
import uuid

from playwright.sync_api import expect


def test_users_list_page_loads(logged_in_page, base_url):
    page = logged_in_page
    page.goto(f"{base_url}/users/")
    expect(page.locator("h1")).to_contain_text("Users")
    expect(page.locator("table")).to_be_visible()


def test_create_clerk_user(logged_in_page, base_url):
    page = logged_in_page
    unique = uuid.uuid4().hex[:6]
    email = f"u-{unique}@test.com"

    page.goto(f"{base_url}/users/create/")
    page.fill("#email", email)
    page.fill("#first_name", "Test")
    page.fill("#last_name", f"Clerk{unique}")
    page.select_option("#role", "clerk")
    page.fill("#phone", "+370600000")

    with page.expect_navigation():
        page.click("button[type='submit']")
    expect(page.locator("table")).to_contain_text(email)


def test_edit_user(logged_in_page, base_url):
    page = logged_in_page
    unique = uuid.uuid4().hex[:6]
    email = f"ue-{unique}@test.com"

    page.goto(f"{base_url}/users/create/")
    page.fill("#email", email)
    page.fill("#first_name", "Before")
    page.fill("#last_name", f"Edit{unique}")
    page.select_option("#role", "clerk")
    with page.expect_navigation():
        page.click("button[type='submit']")

    row = page.locator("tr", has_text=email)
    row.locator("a:has-text('Edit')").click()
    page.wait_for_load_state("networkidle")

    page.fill("#first_name", "After")
    with page.expect_navigation():
        page.click("button[type='submit']")
    expect(page.locator("table")).to_contain_text("After")


def test_deactivate_user(logged_in_page, base_url):
    page = logged_in_page
    unique = uuid.uuid4().hex[:6]
    email = f"ud-{unique}@test.com"

    page.goto(f"{base_url}/users/create/")
    page.fill("#email", email)
    page.fill("#first_name", "Deact")
    page.fill("#last_name", f"User{unique}")
    page.select_option("#role", "clerk")
    with page.expect_navigation():
        page.click("button[type='submit']")

    row = page.locator("tr", has_text=email)
    row.locator("a:has-text('Edit')").click()
    page.wait_for_load_state("networkidle")

    page.on("dialog", lambda d: d.accept())
    with page.expect_navigation():
        page.locator("button:has-text('Deactivate')").click()

    user_row = page.locator("tr", has_text=email)
    expect(user_row).to_contain_text("Inactive")


def test_search_users(logged_in_page, base_url):
    page = logged_in_page
    unique = uuid.uuid4().hex[:6]
    email = f"us-{unique}@test.com"
    last_name = f"Findme{unique}"

    page.goto(f"{base_url}/users/create/")
    page.fill("#email", email)
    page.fill("#first_name", "Searchable")
    page.fill("#last_name", last_name)
    page.select_option("#role", "clerk")
    with page.expect_navigation():
        page.click("button[type='submit']")

    page.goto(f"{base_url}/users/?search={last_name}")
    expect(page.locator("table")).to_contain_text(email)
