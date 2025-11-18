from playwright.sync_api import Page, expect
from scripts.models import User
from scripts.extensions import db
from tests.e2e.conftest import login, get_seeded_object

def test_admin_toggle_user_hidden_status(page: Page, app, seed_data):
    admin = get_seeded_object(app, User, seed_data['admin_ids'][0])
    user_to_toggle = get_seeded_object(app, User, seed_data['user_ids'][2]) # A non-hidden user

    login(page, admin.username, "adminpass")
    page.goto("/admin/users")

    # Find the row for the user to toggle and click it to open the dropdown
    user_row = page.locator(f"tr.user-row[data-user-id='{user_to_toggle.id}']")
    user_row.click() # Click the row to open the dropdown
    
    # Get initial hidden status within app context
    with app.app_context():
        initial_hidden_status = db.session.get(User, user_to_toggle.id).hidden

    # Click the toggle button within the dropdown
    page.locator("#toggle-hidden-button").click()
    page.wait_for_url("/admin/users") # Wait for redirect

    # Expect success flash message on the redirected page
    expect(page.locator(".bg-green-700")).to_be_visible()
    expect(page.locator(".bg-green-700")).to_contain_text(f"User {user_to_toggle.username} hidden status toggled to {not initial_hidden_status}.")

    # Verify status changed in the UI table
    expected_hidden_text = "Yes" if (not initial_hidden_status) else "No"
    expect(user_row.locator("td").nth(5)).to_have_text(expected_hidden_text)

    # Go to scoreboard and verify visibility
    page.goto("/scoreboard")
    if not initial_hidden_status: # If user was visible, now should be hidden
        expect(page.locator(f"text={user_to_toggle.username}")).not_to_be_visible()
    else: # If user was hidden, now should be visible
        expect(page.locator(f"text={user_to_toggle.username}")).to_be_visible()
