from playwright.sync_api import Page, expect
from scripts.models import User
from tests.e2e.conftest import login, get_seeded_object

def test_hidden_user_not_on_scoreboard(page: Page, app, seed_data):
    user = get_seeded_object(app, User, seed_data['user_ids'][0]) # This user is set to hidden in seed_data
    login(page, user.username, "userpass")
    page.goto("/scoreboard")
    expect(page.locator(f"text=/^{user.username}$/")).not_to_be_visible()
