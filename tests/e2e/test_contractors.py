"""E2E tests for contractor management CRUD."""
import uuid

from playwright.sync_api import expect


def test_contractors_list_page_loads(logged_in_page, base_url):
    page = logged_in_page
    page.goto(f"{base_url}/contractors/")
    expect(page.locator("h1")).to_have_text("Contractors")
    expect(page.locator("table")).to_be_visible()


def test_create_contractor(logged_in_page, base_url):
    page = logged_in_page
    unique = uuid.uuid4().hex[:6]
    email = f"c-{unique}@test.com"

    page.goto(f"{base_url}/contractors/create/")
    page.fill("#email", email)
    page.fill("#first_name", "John")
    page.fill("#last_name", f"Doe{unique}")
    page.fill("#phone", "+370611111")
    page.fill("#company_name", f"Corp{unique}")
    page.fill("#bank_name", "Test Bank")
    page.fill("#bank_account", f"LT{unique}0000")
    page.fill("#address", "123 Test St")

    with page.expect_navigation():
        page.click("button[type='submit']")
    expect(page.locator("table")).to_contain_text(email)


def test_edit_contractor(logged_in_page, base_url):
    page = logged_in_page
    unique = uuid.uuid4().hex[:6]
    email = f"ce-{unique}@test.com"

    page.goto(f"{base_url}/contractors/create/")
    page.fill("#email", email)
    page.fill("#first_name", "Edit")
    page.fill("#last_name", f"Con{unique}")
    page.fill("#bank_name", "SomeBank")
    page.fill("#bank_account", f"LT{unique}EDIT")
    page.fill("#address", "456 Edit St")
    with page.expect_navigation():
        page.click("button[type='submit']")

    row = page.locator("tr", has_text=email)
    row.locator("a:has-text('Edit')").click()
    page.wait_for_load_state("networkidle")

    page.fill("#company_name", f"Updated{unique}")
    with page.expect_navigation():
        page.click("button[type='submit']")
    expect(page.locator("table")).to_contain_text(f"Updated{unique}")


def test_deactivate_contractor(logged_in_page, base_url):
    page = logged_in_page
    unique = uuid.uuid4().hex[:6]
    email = f"cd-{unique}@test.com"

    page.goto(f"{base_url}/contractors/create/")
    page.fill("#email", email)
    page.fill("#first_name", "Deact")
    page.fill("#last_name", f"Con{unique}")
    page.fill("#bank_name", "SomeBank")
    page.fill("#bank_account", f"LT{unique}DEACT")
    page.fill("#address", "789 Deact St")
    with page.expect_navigation():
        page.click("button[type='submit']")

    row = page.locator("tr", has_text=email)
    row.locator("a:has-text('Edit')").click()
    page.wait_for_load_state("networkidle")

    page.on("dialog", lambda d: d.accept())
    with page.expect_navigation():
        page.locator("button:has-text('Deactivate')").click()

    contractor_row = page.locator("tr", has_text=email)
    expect(contractor_row).to_contain_text("Inactive")
