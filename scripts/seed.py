from scripts.extensions import db, bcrypt
from scripts.models import User, Category, Challenge, Submission, Setting
from datetime import datetime, UTC, timedelta
import random

def seed_database():
    # Clear existing data
    db.session.query(Submission).delete()
    db.session.query(Challenge).delete()
    db.session.query(Category).delete()
    db.session.query(User).delete()
    db.session.query(Setting).delete()
    db.session.commit()

    # Create 2 Admins
    admin_password = bcrypt.generate_password_hash("adminpass").decode('utf-8')
    admin1 = User(username="admin1", email="admin1@example.com", password_hash=admin_password, is_admin=True, hidden=True, score=0)
    admin2 = User(username="admin2", email="admin2@example.com", password_hash=admin_password, is_admin=True, hidden=True, score=0)
    db.session.add_all([admin1, admin2])
    db.session.commit()

    # Create 24 Users
    users = []
    user_password = bcrypt.generate_password_hash("userpass").decode('utf-8')
    for i in range(1, 25):
        user = User(username=f"user{i}", email=f"user{i}@example.com", password_hash=user_password, is_admin=False, hidden=False, score=0)
        users.append(user)
    db.session.add_all(users)
    db.session.commit()

    # Create 20 Challenges across a few categories
    categories = []
    for i in range(1, 4): # 3 categories
        category = Category(name=f"Category {i}")
        categories.append(category)
    db.session.add_all(categories)
    db.session.commit()

    challenges = []
    for i in range(1, 21): # 20 challenges
        category_id = categories[(i-1) % len(categories)].id
        challenge = Challenge(name=f"Challenge {i}", description=f"Description for Challenge {i}",
                              points=i * 10, flag=f"flag{{{i}}}", category_id=category_id)
        challenges.append(challenge)
    db.session.add_all(challenges)
    db.session.commit()

    # Make users complete challenges
    all_user_challenge_pairs = []
    for user in users:
        for challenge in challenges:
            all_user_challenge_pairs.append((user, challenge))
    
    random.shuffle(all_user_challenge_pairs) # Randomize the order of completions

    submissions_to_add = []
    # Keep track of solved challenges per user to avoid duplicates and control count
    user_solved_challenges = {user.id: set() for user in users}
    
    # To ensure varied scores, let's aim for each user to solve a random number of challenges
    # between, say, 5 and 15 challenges.
    min_challenges_per_user = 5
    max_challenges_per_user = 15

    # Generate submissions
    current_time = datetime.now(UTC)
    time_offset_seconds = 0
    
    for user, challenge in all_user_challenge_pairs:
        if len(user_solved_challenges[user.id]) < random.randint(min_challenges_per_user, max_challenges_per_user):
            if challenge.id not in user_solved_challenges[user.id]:
                submission_time = current_time + timedelta(seconds=time_offset_seconds)
                time_offset_seconds += random.randint(1, 60) # Vary submission times

                # Temporarily update user score for score_at_submission
                user.score += challenge.points
                submission = Submission(user_id=user.id, challenge_id=challenge.id, timestamp=submission_time, score_at_submission=user.score)
                submissions_to_add.append(submission)
                user_solved_challenges[user.id].add(challenge.id)
    
    db.session.add_all(submissions_to_add)
    db.session.commit()

    # Recalculate and update user scores based on actual submissions
    # This is more robust as it reflects the committed submissions
    for user in users:
        user.score = sum(s.challenge_solved.points for s in Submission.query.filter_by(user_id=user.id).all())
    db.session.commit()

    # Set some users to hidden
    users[0].hidden = True
    users[1].hidden = True
    db.session.commit()

    # Add settings
    setting_top_x = Setting(key='TOP_X_SCOREBOARD', value='10')
    setting_graph_type = Setting(key='SCOREBOARD_GRAPH_TYPE', value='line')
    db.session.add_all([setting_top_x, setting_graph_type])
    db.session.commit()

    return {
        "admin_ids": [admin1.id, admin2.id],
        "user_ids": [user.id for user in users],
        "category_ids": [category.id for category in categories],
        "challenge_ids": [challenge.id for challenge in challenges]
    }
