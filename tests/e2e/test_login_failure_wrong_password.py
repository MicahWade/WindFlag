from playwright.sync_api import Page, expect
from scripts.models import User
from tests.e2e.conftest import login, get_seeded_object

def test_login_failure_wrong_password(page: Page, app, seed_data):
    user = get_seeded_object(app, User, seed_data['user_ids'][0])
    login(page, user.username, "wrongpass")
    expect(page).to_have_url("/login")
    expect(page.locator(".bg-red-700")).to_be_visible()
    expect(page.locator(".bg-red-700")).to_have_text("Login Unsuccessful. Please check username and password")
