from playwright.sync_api import Page, expect
from scripts.models import User
from scripts.extensions import db
from tests.e2e.conftest import login, get_seeded_object

def test_admin_toggle_user_admin_status(page: Page, app, seed_data):
    admin = get_seeded_object(app, User, seed_data['admin_ids'][0])
    user_to_toggle = get_seeded_object(app, User, seed_data['user_ids'][3]) # A regular user

    login(page, admin.username, "adminpass")
    page.goto("/admin/users")

    # Find the row for the user to toggle and click it to open the dropdown
    user_row = page.locator(f"tr.user-row[data-user-id='{user_to_toggle.id}']")
    user_row.click() # Click the row to open the dropdown
    with app.app_context():
        initial_admin_status = db.session.get(User, user_to_toggle.id).is_admin

    # Click the toggle button within the dropdown
    page.locator("#toggle-admin-button").click()
    page.wait_for_url("/admin/users") # Wait for redirect

    expect(page.locator(".bg-green-700")).to_be_visible()
    expect(page.locator(".bg-green-700")).to_contain_text(f"User {user_to_toggle.username} admin status toggled to {not initial_admin_status}.")

    # Verify status changed in the UI table
    expected_admin_text = "Yes" if (not initial_admin_status) else "No"
    expect(user_row.locator("td").nth(4)).to_have_text(expected_admin_text)
    # If user was made admin, they should also be hidden
    if not initial_admin_status: # If they became admin
        expect(user_row.locator("td").nth(5)).to_have_text("Yes") # Hidden should be Yes
