from playwright.sync_api import Page, expect
from scripts.models import User, Challenge, Submission, ChallengeFlag
from scripts.extensions import db
from tests.e2e.conftest import login, get_seeded_object

def test_submit_correct_flag(page: Page, app, seed_data):
    user = get_seeded_object(app, User, seed_data['user_ids'][3])
    challenge = get_seeded_object(app, Challenge, seed_data['challenge_ids'][0])
    
    with app.app_context():
        submission = Submission.query.filter_by(user_id=user.id, challenge_id=challenge.id).first()
        if submission:
            db.session.delete(submission)
            db.session.commit()
            user.score -= challenge.points
            db.session.commit()
        
        challenge_flag_obj = ChallengeFlag.query.filter_by(challenge_id=challenge.id).first()
        assert challenge_flag_obj is not None, "Seeded challenge must have at least one flag"
        flag_content = challenge_flag_obj.flag_content

    login(page, user.username, "userpass")
    page.goto("/challenges")
    
    page.locator(f"div.challenge-card[data-id='{challenge.id}']").click()

    # Listen for the dialog (alert)
    page.on("dialog", lambda dialog: dialog.accept()) # Accept the dialog

    page.fill("#modalFlagInput", flag_content)
    page.click("#modalSubmitButton")

    # Explicitly wait for the hidden class to be removed from modalChallengeStatus
    # This ensures Playwright waits until the element is actually visible
    page.wait_for_selector("#modalChallengeStatus:not(.hidden)", state="visible")

    expect(page.locator("#modalChallengeStatus")).to_be_visible()
    expect(page.locator("#modalChallengeStatus")).to_contain_text(f"Correct Flag! Challenge Solved! You earned {challenge.points} points!")
    
    expect(page.locator(f"div.challenge-card[data-id='{challenge.id}']")).to_have_attribute("data-completed", "true")
