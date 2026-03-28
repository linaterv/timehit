"""E2E tests for client management CRUD."""
import uuid

from playwright.sync_api import expect


def test_clients_list_page_loads(logged_in_page, base_url):
    page = logged_in_page
    page.goto(f"{base_url}/clients/")
    expect(page.locator("h1")).to_have_text("Clients")
    expect(page.locator("table")).to_be_visible()


def test_create_client(logged_in_page, base_url):
    page = logged_in_page
    unique = uuid.uuid4().hex[:6]
    company = f"ClientCo{unique}"

    page.goto(f"{base_url}/clients/create/")
    page.fill("#company_name", company)
    page.fill("#billing_address", f"456 Billing St, {unique}")
    page.fill("#tax_id", f"VAT{unique}")
    page.fill("#payment_terms", "45")
    page.fill("#contact_name", f"Jane{unique}")
    page.fill("#contact_email", f"j-{unique}@c.c")
    page.fill("#contact_phone", "+370622222")

    with page.expect_navigation():
        page.click("button[type='submit']")
    expect(page.locator("table")).to_contain_text(company)


def test_edit_client(logged_in_page, base_url):
    page = logged_in_page
    unique = uuid.uuid4().hex[:6]
    company = f"EditCo{unique}"

    page.goto(f"{base_url}/clients/create/")
    page.fill("#company_name", company)
    page.fill("#billing_address", "123 St")
    with page.expect_navigation():
        page.click("button[type='submit']")

    row = page.locator("tr", has_text=company)
    row.locator("a:has-text('Edit')").click()
    page.wait_for_load_state("networkidle")

    new_company = f"Updated{unique}"
    page.fill("#company_name", new_company)
    with page.expect_navigation():
        page.click("button[type='submit']")
    expect(page.locator("table")).to_contain_text(new_company)


def test_deactivate_client(logged_in_page, base_url):
    page = logged_in_page
    unique = uuid.uuid4().hex[:6]
    company = f"DeactCo{unique}"

    page.goto(f"{base_url}/clients/create/")
    page.fill("#company_name", company)
    page.fill("#billing_address", "789 Lane")
    with page.expect_navigation():
        page.click("button[type='submit']")

    row = page.locator("tr", has_text=company)
    row.locator("a:has-text('Edit')").click()
    page.wait_for_load_state("networkidle")

    page.on("dialog", lambda d: d.accept())
    with page.expect_navigation():
        page.locator("button:has-text('Deactivate')").click()

    client_row = page.locator("tr", has_text=company)
    expect(client_row).to_contain_text("Inactive")
