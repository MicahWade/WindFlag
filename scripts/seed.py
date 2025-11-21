"""
This module provides functions to seed the database with initial data
for testing and development purposes.
"""
from scripts.extensions import db, bcrypt
from scripts.models import User, Category, Challenge, Submission, Setting, ChallengeFlag, FlagSubmission, AwardCategory, Award, MULTI_FLAG_TYPES, FlagAttempt, Hint, UserHint
from datetime import datetime, UTC, timedelta
import random

def seed_database():
    """
    Seeds the database with a set of initial users, categories, challenges,
    flags, hints, submissions, and settings for testing and demonstration.
    Existing data for these models will be cleared before seeding.
    """
    # Clear existing data
    db.session.query(FlagAttempt).delete()
    db.session.query(FlagSubmission).delete()
    db.session.query(Submission).delete()
    db.session.query(ChallengeFlag).delete()
    db.session.query(Challenge).delete()
    db.session.query(Category).delete()
    db.session.query(User).delete()
    db.session.query(Setting).delete()
    db.session.query(Award).delete()
    db.session.query(AwardCategory).delete()
    db.session.query(UserHint).delete()
    db.session.query(Hint).delete()
    db.session.commit()

    # Create default Award Categories
    award_category_bug = AwardCategory(name="Bug Report", default_points=50)
    award_category_feature = AwardCategory(name="Feature Suggestion", default_points=30)
    award_category_community = AwardCategory(name="Community Contributor", default_points=100)
    award_category_helpful = AwardCategory(name="Helpful User", default_points=20)
    db.session.add_all([award_category_bug, award_category_feature, award_category_community, award_category_helpful])
    db.session.commit()

    # Create 2 Admins
    admin_password = bcrypt.generate_password_hash("adminpass").decode('utf-8')
    admin1 = User(username="admin1", email="admin1@example.com", password_hash=admin_password, is_admin=True, hidden=True, score=0)
    admin2 = User(username="admin2", email="admin2@example.com", password_hash=admin_password, is_admin=True, hidden=True, score=0)
    
    test_admin_password = bcrypt.generate_password_hash("test").decode('utf-8')
    test_admin_password = bcrypt.generate_password_hash("test").decode('utf-8')
    test_admin = User(username="test", email="test@example.com", password_hash=test_admin_password, is_admin=True, is_super_admin=True, hidden=True, score=0)

    db.session.add_all([admin1, admin2, test_admin])
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
        
        # Determine multi_flag_type and threshold
        multi_flag_type = random.choice(MULTI_FLAG_TYPES)
        num_flags_for_challenge = random.randint(1, 3) # 1 to 3 flags per challenge for seeding
        multi_flag_threshold = None

        multi_flag_threshold = None
        point_decay_type = 'FLAT'
        point_decay_rate = 0
        point_decay_every_solve = False

        if i % 3 == 0:
            point_decay_type = 'LINEAR'
            point_decay_rate = 5
            point_decay_every_solve = True
        elif i % 3 == 1:
            point_decay_type = 'EXPONENTIAL'
            point_decay_rate = 1
        
        if multi_flag_type == 'SINGLE':
            num_flags_for_challenge = 1
        elif multi_flag_type == 'N_OF_M':
            multi_flag_threshold = random.randint(1, num_flags_for_challenge) # N must be <= M

        challenge = Challenge(name=f"Challenge {i}", description=f"Description for Challenge {i}",
                              points=i * 10, case_sensitive=True, category_id=category_id,
                              multi_flag_type=multi_flag_type, multi_flag_threshold=multi_flag_threshold,
                              point_decay_type=point_decay_type, point_decay_rate=point_decay_rate)
        challenges.append(challenge)
        db.session.add(challenge) # Add challenge to session

    db.session.commit() # Commit all challenges to get their IDs

    challenge_flags = []
    for challenge in challenges: # Iterate through committed challenges
        # Re-determine num_flags based on challenge type for consistency with how flags are generated
        num_flags_to_create = 1 # Default for SINGLE
        if challenge.multi_flag_type == 'ANY' or challenge.multi_flag_type == 'ALL':
            num_flags_to_create = random.randint(1, 3)
        elif challenge.multi_flag_type == 'N_OF_M':
            # Ensure enough flags for N_OF_M, at least the threshold
            num_flags_to_create = random.randint(challenge.multi_flag_threshold, 3) if challenge.multi_flag_threshold else 1

        for j in range(num_flags_to_create):
            flag_content = f"flag{{{challenge.id}-{j+1}}}"
            challenge_flag = ChallengeFlag(challenge_id=challenge.id, flag_content=flag_content)
            challenge_flags.append(challenge_flag)
    
    db.session.add_all(challenge_flags)
    db.session.commit()

    # Generate Hints for Challenges
    hints_to_add = []
    for challenge in challenges:
        num_hints = random.randint(0, 2) # 0 to 2 hints per challenge
        for i in range(num_hints):
            # Hint cost can be a percentage of challenge points, e.g., 10-30%
            hint_cost = int(challenge.points * random.uniform(0.1, 0.3))
            hint_title = f"Hint {i+1} for {challenge.name}"
            hint_content = f"This is hint {i+1} for Challenge {challenge.name}. It costs {hint_cost} points."
            hint = Hint(challenge_id=challenge.id, title=hint_title, content=hint_content, cost=hint_cost)
            hints_to_add.append(hint)
    db.session.add_all(hints_to_add)
    db.session.commit()

    # Generate submissions
    # Start submissions from a few weeks ago
    start_date = datetime.now(UTC) - timedelta(weeks=3)
    
    submissions_to_add = []
    flag_submissions_to_add = []
    flag_attempts_to_add = []
    
    min_challenges_per_user = 5
    max_challenges_per_user = 15

    for user in users:
        user_current_score = 0
        user_solved_challenges_ids = set()
        
        # Initialize last_submission_time for this user
        last_submission_time = start_date
        
        # Select a random subset of challenges for this user to solve
        num_challenges_to_solve = random.randint(min_challenges_per_user, max_challenges_per_user)
        
        # Shuffle challenges and pick the first 'num_challenges_to_solve'
        # Sort them by ID to ensure a consistent (monotonic) score progression
        challenges_for_user = random.sample(challenges, min(num_challenges_to_solve, len(challenges)))
        challenges_for_user.sort(key=lambda c: c.id) # Sort by challenge ID for consistent progression

        # Generate submissions for this user
        for challenge in challenges_for_user:
            if challenge.id not in user_solved_challenges_ids:
                # Generate a submission time that is strictly after the last one for this user
                # Add a random timedelta between 1 hour and 2 days to the last submission time
                time_delta = timedelta(hours=random.randint(1, 48))
                submission_time = last_submission_time + time_delta
                last_submission_time = submission_time # Update last_submission_time for the next submission

                user_current_score += challenge.points
                submission = Submission(user_id=user.id, challenge_id=challenge.id, timestamp=submission_time, score_at_submission=user_current_score)
                submissions_to_add.append(submission)
                user_solved_challenges_ids.add(challenge.id)

                # Create FlagSubmission entries for all flags of this challenge
                db.session.refresh(challenge) # Refresh to load flags relationship
                for flag in challenge.flags:
                    flag_submission = FlagSubmission(user_id=user.id, challenge_id=challenge.id,
                                                     challenge_flag_id=flag.id, timestamp=submission_time)
                    flag_submissions_to_add.append(flag_submission)

                    # Also create a successful FlagAttempt for this correct flag
                    successful_flag_attempt = FlagAttempt(
                        user_id=user.id,
                        challenge_id=challenge.id,
                        submitted_flag=flag.flag_content, # The correct flag content
                        is_correct=True,
                        timestamp=submission_time
                    )
                    flag_attempts_to_add.append(successful_flag_attempt) # Add to the list that gets committed later
    
    db.session.add_all(submissions_to_add)
    db.session.add_all(flag_submissions_to_add)
    db.session.commit()

    # Generate some failed attempts
    for user in users:
        # For each user, pick a few challenges they did NOT solve
        unsolved_challenges = [c for c in challenges if c.id not in user_solved_challenges_ids]
        
        # Attempt a few random unsolved challenges
        num_failed_attempts = random.randint(0, min(5, len(unsolved_challenges))) # 0 to 5 failed attempts per user
        
        for _ in range(num_failed_attempts):
            if not unsolved_challenges:
                break
            
            challenge_for_attempt = random.choice(unsolved_challenges)
            unsolved_challenges.remove(challenge_for_attempt) # Ensure unique challenges for failed attempts

            # Generate a random incorrect flag content
            incorrect_flag_content = f"wrong_flag{{{challenge_for_attempt.id}}}-{random.randint(100, 999)}"
            
            # Generate a timestamp for the failed attempt
            # It should be within the general submission timeframe
            attempt_time = start_date + timedelta(days=random.randint(0, 20))

            failed_attempt = FlagAttempt(
                user_id=user.id,
                challenge_id=challenge_for_attempt.id,
                submitted_flag=incorrect_flag_content,
                is_correct=False,
                timestamp=attempt_time
            )
            flag_attempts_to_add.append(failed_attempt)
    
    db.session.add_all(flag_attempts_to_add)
    db.session.commit()

    # Recalculate and update user scores based on actual submissions
    # This is more robust as it reflects the committed submissions
    for user in users:
        user.score = sum(s.challenge_rel.points for s in Submission.query.filter_by(user_id=user.id).all())
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
        "admin_ids": [admin1.id, admin2.id, test_admin.id],
        "user_ids": [user.id for user in users],
        "category_ids": [category.id for category in categories],
        "challenge_ids": [challenge.id for challenge in challenges]
    }