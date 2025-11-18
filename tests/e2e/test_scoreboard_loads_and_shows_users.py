import re
from playwright.sync_api import Page, expect
from scripts.models import User
from tests.e2e.conftest import login, get_seeded_object

def test_scoreboard_loads_and_shows_users(page: Page, app, seed_data):
    user = get_seeded_object(app, User, seed_data['user_ids'][0])
    login(page, user.username, "userpass")
    page.goto("/scoreboard")
    expect(page).to_have_title(re.compile("Scoreboard"))
    expect(page.locator("h1")).to_have_text("Scoreboard")

    with app.app_context():
        all_users = User.query.all()
        all_admins = User.query.filter_by(is_admin=True).all() # Assuming admins are also users

    # Check if non-hidden users are visible
    for u in all_users:
        if not u.hidden:
            expect(page.locator(f"text=/^{u.username}$/")).to_be_visible() # Use exact text match
    
    # Check that hidden users are NOT visible
    for u in all_users:
        if u.hidden:
            expect(page.locator(f"text=/^{u.username}$/")).not_to_be_visible() # Use exact text match
    for admin in all_admins:
        if admin.hidden: # Admins are hidden by default in seed_data
            expect(page.locator(f"text=/^{admin.username}$/")).not_to_be_visible() # Use exact text match
