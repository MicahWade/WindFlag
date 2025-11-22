"""
This module provides functions to seed the database with initial data
for testing and development purposes.
"""
from scripts.extensions import db, bcrypt
from scripts.models import User, Category, Challenge, Submission, Setting, ChallengeFlag, FlagSubmission, AwardCategory, Award, MULTI_FLAG_TYPES, FlagAttempt, Hint, UserHint
from datetime import datetime, UTC, timedelta
import random
import secrets
import hashlib

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
    db.session.query(UserHint).delete()
    db.session.query(Hint).delete()
    db.session.query(Challenge).delete()
    db.session.query(Category).delete()
    db.session.query(Award).delete()
    db.session.query(AwardCategory).delete()
    db.session.query(User).delete()
    db.session.query(Setting).delete()
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

    # Create users from the generated usernames
    from scripts.utils import generate_usernames
    from flask import current_app
    
    users = []
    generated_usernames = generate_usernames()
    user_password = bcrypt.generate_password_hash("userpass").decode('utf-8')

    for username in generated_usernames:
        user = User(username=username, email=f"{username}@example.com", password_hash=user_password, is_admin=False, hidden=False, score=0)
        users.append(user)
    
    # Add specific user "zen"
    zen_password = bcrypt.generate_password_hash("zen").decode('utf-8')
    zen_user = User(username="zen", email="zen@example.com", password_hash=zen_password, is_admin=False, hidden=False, score=0)
    users.append(zen_user)

    db.session.add_all(users)
    db.session.commit()

    # Create 20 Challenges across a few categories
    categories = []
    for i in range(1, 4): # 3 categories
        category = Category(name=f"Category {i}")
        categories.append(category)
    
    # Add a new hidden category
    hidden_category = Category(name="Hidden Category", is_hidden=True, unlock_type='HIDDEN')
    categories.append(hidden_category)

    db.session.add_all(categories)
    db.session.commit()

    challenges = []
    
    # --- Create a DYNAMIC Challenge ---
    dynamic_api_key = secrets.token_hex(16)
    dynamic_api_key_hash = hashlib.sha256(dynamic_api_key.encode('utf-8')).hexdigest()
    dynamic_challenge = Challenge(name="Dynamic Challenge", description="This challenge has a dynamic flag.",
                                  points=100, case_sensitive=True, category_id=categories[0].id,
                                  multi_flag_type='DYNAMIC', dynamic_flag_api_key_hash=dynamic_api_key_hash)
    print(f"Dynamic Challenge API Key: {dynamic_api_key}")
    challenges.append(dynamic_challenge)
    db.session.add(dynamic_challenge)

    # --- Create an HTTP Challenge ---
    http_challenge = Challenge(name="HTTP Challenge", description="This challenge flag is retrieved from a remote URL.",
                               points=100, case_sensitive=True, category_id=categories[1].id,
                               multi_flag_type='HTTP')
    challenges.append(http_challenge)
    db.session.add(http_challenge)

    # --- Create a TIMED Challenge ---
    timed_challenge = Challenge(name="Timed Challenge", description="This challenge will be available in the future.",
                                points=100, case_sensitive=True, category_id=categories[2].id,
                                unlock_type='TIMED', unlock_date_time=datetime.now(UTC) + timedelta(days=1))
    challenges.append(timed_challenge)
    db.session.add(timed_challenge)
    
    # --- Create a Challenge with Proactive Decay ---
    proactive_decay_challenge = Challenge(name="Proactive Decay Challenge", description="This challenge has proactive point decay.",
                                          points=200, case_sensitive=True, category_id=categories[0].id,
                                          point_decay_type='LINEAR', point_decay_rate=10, proactive_decay=True)
    challenges.append(proactive_decay_challenge)
    db.session.add(proactive_decay_challenge)

    for i in range(1, 17): # 16 more challenges to make it 20
        category_id = categories[(i-1) % len(categories)].id
        
        multi_flag_type = random.choice(MULTI_FLAG_TYPES)
        num_flags_for_challenge = random.randint(1, 3) 
        multi_flag_threshold = None

        point_decay_type = 'STATIC'
        point_decay_rate = None
        proactive_decay = False

        if i % 3 == 0:
            point_decay_type = 'LINEAR'
            point_decay_rate = 5
            proactive_decay = True
        elif i % 3 == 1:
            point_decay_type = 'LOGARITHMIC'
            point_decay_rate = 1
        
        if multi_flag_type == 'SINGLE':
            num_flags_for_challenge = 1
        elif multi_flag_type == 'N_OF_M':
            multi_flag_threshold = random.randint(1, num_flags_for_challenge)

        is_hidden = False
        unlock_type = 'NONE'
        prerequisite_count_value = None
        prerequisite_percentage_value = None
        prerequisite_count_category_ids = None
        prerequisite_challenge_ids = None
        
        challenge_name = f"Challenge {i}"

        if i == 1: # Challenge 1: Hidden for all users
            is_hidden = True
            challenge_name = "Hidden Challenge (Admin Only)"
        elif i == 2: # Challenge 2: Locked by Prerequisites (Count for Category 1)
            unlock_type = 'PREREQUISITE_COUNT'
            prerequisite_count_value = 1 
            prerequisite_count_category_ids = [categories[0].id] # Requires 1 challenge from Category 1
            challenge_name = "Locked by Prereq (Cat Count)"
        elif i == 3: # Challenge 3: Locked by Prerequisites (Percentage, e.g., 10%)
            unlock_type = 'PREREQUISITE_PERCENTAGE'
            prerequisite_percentage_value = 10 
            challenge_name = "Locked by Prereq (Percentage)"

        challenge = Challenge(name=challenge_name, description=f"Description for {challenge_name}",
                              points=i * 10, case_sensitive=True, category_id=category_id,
                              multi_flag_type=multi_flag_type, multi_flag_threshold=multi_flag_threshold,
                              point_decay_type=point_decay_type, point_decay_rate=point_decay_rate,
                              proactive_decay=proactive_decay, is_hidden=is_hidden,
                              unlock_type=unlock_type, prerequisite_count_value=prerequisite_count_value,
                              prerequisite_percentage_value=prerequisite_percentage_value,
                              prerequisite_count_category_ids=prerequisite_count_category_ids,
                              prerequisite_challenge_ids=prerequisite_challenge_ids)
        challenges.append(challenge)
        db.session.add(challenge) # Add challenge to session
    
    db.session.commit()

    challenge_flags = []
    for challenge in challenges: 
        if challenge.multi_flag_type not in ['DYNAMIC', 'HTTP']:
            num_flags_to_create = 1 
            if challenge.multi_flag_type == 'ANY' or challenge.multi_flag_type == 'ALL':
                num_flags_to_create = random.randint(1, 3)
            elif challenge.multi_flag_type == 'N_OF_M':
                multi_flag_threshold = challenge.multi_flag_threshold if challenge.multi_flag_threshold else 1
                num_flags_to_create = random.randint(multi_flag_threshold, multi_flag_threshold + 2) # Ensure enough flags for N_OF_M
                if num_flags_to_create < multi_flag_threshold: # Just in case random is too low
                    num_flags_to_create = multi_flag_threshold

            for j in range(num_flags_to_create):
                flag_content = f"flag{{{challenge.id}-{j+1}}}"
                challenge_flag = ChallengeFlag(challenge_id=challenge.id, flag_content=flag_content)
                challenge_flags.append(challenge_flag)
    
    db.session.add_all(challenge_flags)
    db.session.commit()

    # Generate Hints for Challenges
    hints_to_add = []
    for challenge in challenges:
        num_hints = random.randint(0, 2)
        for i in range(num_hints):
            hint_cost = int(challenge.points * random.uniform(0.1, 0.3))
            hint_title = f"Hint {i+1} for {challenge.name}"
            hint_content = f"This is hint {i+1} for Challenge {challenge.name}. It costs {hint_cost} points."
            hint = Hint(challenge_id=challenge.id, title=hint_title, content=hint_content, cost=hint_cost)
            hints_to_add.append(hint)
    db.session.add_all(hints_to_add)
    db.session.commit()

    # Generate submissions
    start_date = datetime.now(UTC) - timedelta(weeks=3)
    
    submissions_to_add = []
    flag_submissions_to_add = []
    flag_attempts_to_add = []
    user_hints_to_add = []
    
    for user in users:
        user_current_score = 0
        solved_challenges_ids = set()
        last_submission_time = start_date

        num_challenges_to_solve = random.randint(5, 15)
        
        challenges_for_user = random.sample(challenges, num_challenges_to_solve)
        challenges_for_user.sort(key=lambda c: c.id)

        for challenge in challenges_for_user:
            if challenge.id in solved_challenges_ids or challenge.multi_flag_type in ['DYNAMIC', 'HTTP']:
                continue

            time_delta = timedelta(hours=random.randint(1, 48))
            submission_time = last_submission_time + time_delta
            last_submission_time = submission_time 

            user_current_score += challenge.points
            submissions_to_add.append(Submission(user_id=user.id, challenge_id=challenge.id, timestamp=submission_time, score_at_submission=user_current_score))
            solved_challenges_ids.add(challenge.id)
            
            db.session.refresh(challenge)
            for flag in challenge.flags:
                flag_submissions_to_add.append(FlagSubmission(user_id=user.id, challenge_id=challenge.id, challenge_flag_id=flag.id, timestamp=submission_time))
                flag_attempts_to_add.append(FlagAttempt(user_id=user.id, challenge_id=challenge.id, submitted_flag=flag.flag_content, is_correct=True, timestamp=submission_time))

            for hint in challenge.hints:
                if random.random() < 0.3: # 30% chance to unlock a hint
                    user_hints_to_add.append(UserHint(user_id=user.id, hint_id=hint.id, timestamp=submission_time - timedelta(minutes=10)))
                    user_current_score -= hint.cost

        user.score = user_current_score

    db.session.add_all(submissions_to_add)
    db.session.add_all(flag_submissions_to_add)
    db.session.add_all(flag_attempts_to_add)
    db.session.add_all(user_hints_to_add)
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