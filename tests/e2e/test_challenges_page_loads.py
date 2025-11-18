import re
from playwright.sync_api import Page, expect
from scripts.models import User
from tests.e2e.conftest import login, get_seeded_object

def test_challenges_page_loads(page: Page, app, seed_data):
    user = get_seeded_object(app, User, seed_data['user_ids'][0])
    login(page, user.username, "userpass")
    page.goto("/challenges")
    expect(page).to_have_title(re.compile("Challenges"))
    expect(page.locator("h1")).to_have_text("Challenges")
    # Check if at least one category is displayed
    expect(page.locator("h2.text-2xl").first).to_be_visible()
    # Check if at least one challenge is displayed
    expect(page.locator("h5.text-xl").first).to_be_visible()
