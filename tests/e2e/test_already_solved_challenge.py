from playwright.sync_api import Page, expect
from scripts.models import User, Challenge, Submission
from scripts.extensions import db
from tests.e2e.conftest import login, get_seeded_object
from datetime import datetime, UTC

def test_already_solved_challenge(page: Page, app, seed_data):
    user = get_seeded_object(app, User, seed_data['user_ids'][5])
    challenge = get_seeded_object(app, Challenge, seed_data['challenge_ids'][2])

    # Ensure user has solved this challenge
    with app.app_context():
        submission = Submission.query.filter_by(user_id=user.id, challenge_id=challenge.id).first()
        if not submission:
            user.score += challenge.points
            new_submission = Submission(user_id=user.id, challenge_id=challenge.id, timestamp=datetime.now(UTC), score_at_submission=user.score)
            db.session.add(new_submission)
            db.session.commit()

    login(page, user.username, "userpass")
    page.goto("/challenges")

    # Click the challenge card to open the modal
    page.locator(f"div.challenge-card[data-id='{challenge.id}']").click()
    page.wait_for_selector("#challengeModal", state="visible") # Wait for modal to be visible

    # Assert that the input and submit button are disabled
    expect(page.locator("#modalFlagInput")).to_be_disabled()
    expect(page.locator("#modalSubmitButton")).to_be_disabled()

    # Expect message indicating already solved within the modal
    expect(page.locator("#modalChallengeStatus")).to_be_visible()
    expect(page.locator("#modalChallengeStatus")).to_have_text("You have already completed this challenge!")
