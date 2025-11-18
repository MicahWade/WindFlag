from playwright.sync_api import Page, expect
from scripts.models import User
from tests.e2e.conftest import login, get_seeded_object

def test_admin_login_success(page: Page, app, seed_data):
    admin = get_seeded_object(app, User, seed_data['admin_ids'][0])
    login(page, admin.username, "adminpass")
    expect(page).to_have_url("/profile")
    expect(page.locator("h1")).to_have_text(f"{admin.username}'s Profile")
    # Verify admin link is visible
    expect(page.get_by_role("link", name="Admin")).to_be_visible()
