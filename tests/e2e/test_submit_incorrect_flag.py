from playwright.sync_api import Page, expect
from scripts.models import User, Challenge, Submission
from scripts.extensions import db
from tests.e2e.conftest import login, get_seeded_object

def test_submit_incorrect_flag(page: Page, app, seed_data):
    page.on("dialog", lambda dialog: dialog.accept()) # Automatically accept dialogs
    user = get_seeded_object(app, User, seed_data['user_ids'][4])
    challenge = get_seeded_object(app, Challenge, seed_data['challenge_ids'][1])

    # Ensure user has not solved this challenge yet
    with app.app_context():
        submission = Submission.query.filter_by(user_id=user.id, challenge_id=challenge.id).first()
        if submission:
            db.session.delete(submission)
            db.session.commit()
            user.score -= challenge.points # Adjust score if submission existed
            db.session.commit()

    login(page, user.username, "userpass")
    page.goto("/challenges")

    # Click the challenge card to open the modal
    page.locator(f"div.challenge-card[data-id='{challenge.id}']").click()
    page.wait_for_selector("#challengeModal", state="visible") # Wait for modal to be visible

    expect(page.locator("#modalFlagInput")).to_be_enabled() # Assert input is enabled
    page.fill("#modalFlagInput", "incorrect_flag")
    page.click("#modalSubmitButton")
