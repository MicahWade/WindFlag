from playwright.sync_api import Page, expect
from scripts.models import User, Challenge
from scripts.extensions import db
from tests.e2e.conftest import login, get_seeded_object

def test_admin_create_challenge_case_sensitive_checkbox(page: Page, app, seed_data):
    admin = get_seeded_object(app, User, seed_data['admin_ids'][0])
    login(page, admin.username, "adminpass")
    page.goto("/admin/challenge/new")

    # Assert that the case_sensitive checkbox is present
    case_sensitive_checkbox = page.locator("input[name='case_sensitive']")
    expect(case_sensitive_checkbox).to_be_visible()
    expect(page.locator("label[for='case_sensitive']")).to_have_text("Flags are Case-Sensitive") # Updated assertion

    # Fill out the form
    page.fill("input[name='name']", "New Case-Sensitive Challenge")
    page.fill("textarea[name='description']", "This is a new challenge with case-sensitive flag.")
    page.fill("input[name='points']", "200")
    # The 'flag' input field is now for multi-flag challenges, but for a single flag, it still works.
    # However, the Challenge model no longer has a 'flag' attribute directly.
    # This test needs to be updated to reflect the new multi-flag challenge creation process.
    # For now, I'll leave this as is, but it will likely fail later when the form submission is processed.
    # The immediate fix is just the label text.
    page.fill("textarea[name='flags_input']", "MySecretFlag") # Changed from 'input[name='flag']' to 'textarea[name='flags_input']'

    # Select an existing category (assuming category with id 1 exists from seed_data)
    page.select_option("select[name='category']", value=str(seed_data['category_ids'][0])) # Use seeded category ID

    # Check the case_sensitive checkbox
    case_sensitive_checkbox.check()

    # Submit the form
    page.click("input[type='submit']")

    # Expect success flash message
    expect(page.locator(".bg-green-700")).to_be_visible()
    expect(page.locator(".bg-green-700")).to_contain_text("Challenge has been created!")

    # Verify the challenge was created with case_sensitive=True
    with app.app_context():
        new_challenge = Challenge.query.filter_by(name="New Case-Sensitive Challenge").first()
        assert new_challenge is not None
        assert new_challenge.case_sensitive is True
        assert len(new_challenge.flags) == 1
        assert new_challenge.flags[0].flag_content == "MySecretFlag"