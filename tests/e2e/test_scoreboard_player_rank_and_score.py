from playwright.sync_api import Page, expect
from scripts.models import User, Challenge, Submission
from scripts.extensions import db
from tests.e2e.conftest import login, get_seeded_object
from sqlalchemy import func

def test_scoreboard_player_rank_and_score(page: Page, app, seed_data):
    user = get_seeded_object(app, User, seed_data['user_ids'][0])
    login(page, user.username, "userpass")
    page.goto("/scoreboard")

    # Fetch users from the database, ordered by score and then submission timestamp for accurate ranking
    with app.app_context():
        # Replicate the scoreboard_data API logic for ranking
        expected_ranked_users_data = db.session.query(
            User.username,
            func.coalesce(func.sum(Challenge.points), 0).label('score'),
            func.max(Submission.timestamp).label('last_submission')
        ).outerjoin(Submission, User.id == Submission.user_id)\
         .outerjoin(Challenge, Submission.challenge_id == Challenge.id)\
         .filter(User.hidden == False)\
         .group_by(User.id, User.username)\
         .order_by(func.coalesce(func.sum(Challenge.points), 0).desc(), func.max(Submission.timestamp).asc())\
         .all()

    # Verify ranks and scores
    for i, user_data in enumerate(expected_ranked_users_data):
        # Find the row for the user
        user_row = page.locator(f"tr:has-text('{user_data.username}')")
        actual_score_text = user_row.locator("td").nth(2).text_content()
        print(f"User: {user_data.username}, Expected Rank: {i+1}, Actual Rank: {user_row.locator('td').nth(0).text_content()}, Expected Score: {user_data.score}, Actual Score: {actual_score_text}")
        expect(user_row.locator("td").nth(0)).to_have_text(str(i + 1)) # Rank
        expect(user_row.locator("td").nth(1)).to_have_text(user_data.username) # Username
        expect(user_row.locator("td").nth(2)).to_have_text(str(user_data.score)) # Score
