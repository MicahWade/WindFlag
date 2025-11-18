from playwright.sync_api import Page, expect
from tests.e2e.conftest import login

def test_login_failure_non_existent_user(page: Page):
    login(page, "nonexistent", "password")
    expect(page).to_have_url("/login")
    expect(page.locator(".bg-red-700")).to_be_visible()
    expect(page.locator(".bg-red-700")).to_have_text("Login Unsuccessful. Please check username and password")
