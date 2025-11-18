from playwright.sync_api import Page, expect
from scripts.models import User
from tests.e2e.conftest import login, get_seeded_object

def test_login_success(page: Page, app, seed_data):
    user = get_seeded_object(app, User, seed_data['user_ids'][2]) # Use a non-hidden user
    login(page, user.username, "userpass")
    expect(page).to_have_url("/profile")
    expect(page.locator("h1")).to_have_text(f"{user.username}'s Profile")
