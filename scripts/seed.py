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
    db.session.add_all(categories)
    db.session.commit()

    challenges = []
    # Create the prerequisite challenge for the "Rarely Unlocked" challenge
    prereq_for_rarely_unlocked = Challenge(name="Prerequisite for Rarely Unlocked", description="Solve this to unlock the rarely unlocked challenge.",
                                          points=50, case_sensitive=True, category_id=categories[0].id,
                                          multi_flag_type='SINGLE')
    db.session.add(prereq_for_rarely_unlocked)
    db.session.commit() # Commit to get its ID

    for i in range(1, 21): # Existing 20 challenges
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
    
    # Add the "Rarely Unlocked" challenge
    rarely_unlocked_challenge = Challenge(name="Rarely Unlocked Challenge",
                                          description="This challenge is only unlocked if you solve the 'Prerequisite for Rarely Unlocked' challenge.",
                                          points=150, case_sensitive=True, category_id=categories[0].id,
                                          multi_flag_type='SINGLE',
                                          unlock_type='PREREQUISITE_COUNT', # Assuming PREREQUISITE_COUNT can also use specific IDs
                                          prerequisite_count_value=1, # Requires one specific challenge
                                          prerequisite_challenge_ids=[prereq_for_rarely_unlocked.id])
    db.session.add(rarely_unlocked_challenge)
    challenges.append(rarely_unlocked_challenge) # Add to the list of all challenges

    # Add a challenge specifically for the Blue Stripe (Rarely Unlocked)
    blue_stripe_prereq = Challenge(name="Blue Stripe Prerequisite", description="Solve this for the blue stripe challenge.",
                                   points=20, case_sensitive=True, category_id=categories[1].id,
                                   multi_flag_type='SINGLE')
    db.session.add(blue_stripe_prereq)
    db.session.commit() # Commit to get its ID

    blue_stripe_challenge = Challenge(name="Blue Stripe Challenge",
                                      description="This challenge should have a blue stripe (Rarely Unlocked).",
                                      points=100, case_sensitive=True, category_id=categories[1].id,
                                      multi_flag_type='SINGLE',
                                      unlock_type='PREREQUISITE_COUNT',
                                      prerequisite_count_value=1,
                                      prerequisite_challenge_ids=[blue_stripe_prereq.id])
    db.session.add(blue_stripe_challenge)
    challenges.append(blue_stripe_challenge) # Add to the list of all challenges

    db.session.commit() # Commit all challenges to get their IDs and ensure prereq_for_rarely_unlocked has an ID

    # --- After challenges are committed, link prerequisites and ensure specific submissions ---
    # Now that all challenges have IDs, update the `prerequisite_challenge_ids` for the rarely unlocked one properly
    # (This was done during creation now, but leaving this comment as a reminder for complex cross-references)
    
    challenge_flags = []
    # Include the new prerequisite and rarely unlocked challenges in flag generation
    all_challenges_for_flags = [prereq_for_rarely_unlocked, rarely_unlocked_challenge, blue_stripe_prereq, blue_stripe_challenge] + challenges 
    for challenge in all_challenges_for_flags: 
        num_flags_to_create = 1 
        if challenge.multi_flag_type == 'ANY' or challenge.multi_flag_type == 'ALL':
            num_flags_to_create = random.randint(1, 3)
        elif challenge.multi_flag_type == 'N_OF_M':
            num_flags_to_create = random.randint(challenge.multi_flag_threshold if challenge.multi_flag_threshold else 1, 3)

        for j in range(num_flags_to_create):
            flag_content = f"flag{{{challenge.id}-{j+1}}}"
            challenge_flag = ChallengeFlag(challenge_id=challenge.id, flag_content=flag_content)
            challenge_flags.append(challenge_flag)
    
    db.session.add_all(challenge_flags)
    db.session.commit()

    # Generate Hints for Challenges
    hints_to_add = []
    for challenge in all_challenges_for_flags:
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
    
    min_challenges_per_user = 5
    max_challenges_per_user = 15

    # Specific user actions to guarantee stripe types
    # User 1 will solve the prerequisite for the "Rarely Unlocked" challenge
    user1_obj = users[0]
    user1_obj.score += prereq_for_rarely_unlocked.points # Manually adjust score
    submission_time_user1 = start_date + timedelta(hours=random.randint(1, 24))
    submissions_to_add.append(Submission(user_id=user1_obj.id, challenge_id=prereq_for_rarely_unlocked.id, timestamp=submission_time_user1, score_at_submission=user1_obj.score))
    
    prereq_for_rarely_unlocked_flags = ChallengeFlag.query.filter_by(challenge_id=prereq_for_rarely_unlocked.id).all()
    for flag in prereq_for_rarely_unlocked_flags:
        flag_submissions_to_add.append(FlagSubmission(user_id=user1_obj.id, challenge_id=prereq_for_rarely_unlocked.id, challenge_flag_id=flag.id, timestamp=submission_time_user1))
        flag_attempts_to_add.append(FlagAttempt(user_id=user1_obj.id, challenge_id=prereq_for_rarely_unlocked.id, submitted_flag=flag.flag_content, is_correct=True, timestamp=submission_time_user1))

    # User 2 and User 3 will solve the prerequisite for the "Blue Stripe Challenge"
    user2_obj = users[1]
    user3_obj = users[2]

    user2_obj.score += blue_stripe_prereq.points
    submission_time_user2 = start_date + timedelta(hours=random.randint(1, 24))
    submissions_to_add.append(Submission(user_id=user2_obj.id, challenge_id=blue_stripe_prereq.id, timestamp=submission_time_user2, score_at_submission=user2_obj.score))
    blue_stripe_prereq_flags = ChallengeFlag.query.filter_by(challenge_id=blue_stripe_prereq.id).all()
    for flag in blue_stripe_prereq_flags:
        flag_submissions_to_add.append(FlagSubmission(user_id=user2_obj.id, challenge_id=blue_stripe_prereq.id, challenge_flag_id=flag.id, timestamp=submission_time_user2))
        flag_attempts_to_add.append(FlagAttempt(user_id=user2_obj.id, challenge_id=blue_stripe_prereq.id, submitted_flag=flag.flag_content, is_correct=True, timestamp=submission_time_user2))

    user3_obj.score += blue_stripe_prereq.points
    submission_time_user3 = start_date + timedelta(hours=random.randint(1, 24))
    submissions_to_add.append(Submission(user_id=user3_obj.id, challenge_id=blue_stripe_prereq.id, timestamp=submission_time_user3, score_at_submission=user3_obj.score))
    for flag in blue_stripe_prereq_flags:
        flag_submissions_to_add.append(FlagSubmission(user_id=user3_obj.id, challenge_id=blue_stripe_prereq.id, challenge_flag_id=flag.id, timestamp=submission_time_user3))
        flag_attempts_to_add.append(FlagAttempt(user_id=user3_obj.id, challenge_id=blue_stripe_prereq.id, submitted_flag=flag.flag_content, is_correct=True, timestamp=submission_time_user3))


    # All other users will have random submissions, but *not* the prerequisite for rarely unlocked,
    # and *not* Challenge 2 (Locked by Prereq - Cat Count) for categories[0].id
    # Ensure they solve some general challenges so their percentage for Challenge 3 can be met.
    
    # Store challenge IDs to control which ones get solved
    challenge_ids_to_avoid_for_most_users = {prereq_for_rarely_unlocked.id, blue_stripe_prereq.id, Challenge.query.filter_by(name="Locked by Prereq (Cat Count)").first().id}
    
    # For Challenge 3, ensure some users meet the 10% percentage
    solved_percentage_target_challenges_users = users[1:5] # Users 2, 3, 4, 5
    num_other_challenges = len(all_challenges_for_flags) - len(challenge_ids_to_avoid_for_most_users)
    
    for user in users:
        if user.id == user1_obj.id or user.id == user2_obj.id or user.id == user3_obj.id: # Skip users with specific submissions
            continue

        user_current_score = user.score # Start with existing score if any
        user_solved_challenges_ids = {s.challenge_id for s in Submission.query.filter_by(user_id=user.id).all()}
        last_submission_time = start_date # Reset for each user

        # Select a random subset of challenges for this user to solve, avoiding specific ones
        # and ensuring they solve enough for Challenge 3 to be potentially unlocked.
        candidate_challenges = [c for c in all_challenges_for_flags if c.id not in challenge_ids_to_avoid_for_most_users and not c.is_hidden and c.id not in user_solved_challenges_ids]
        
        num_challenges_to_solve = random.randint(min(5, len(candidate_challenges)), min(max_challenges_per_user, len(candidate_challenges)))
        
        challenges_for_user_subset = random.sample(candidate_challenges, num_challenges_to_solve)
        challenges_for_user_subset.sort(key=lambda c: c.id)

        for challenge in challenges_for_user_subset:
            # Generate a submission time that is strictly after the last one for this user
            time_delta = timedelta(hours=random.randint(1, 48))
            submission_time = last_submission_time + time_delta
            last_submission_time = submission_time 

            user_current_score += challenge.points
            submissions_to_add.append(Submission(user_id=user.id, challenge_id=challenge.id, timestamp=submission_time, score_at_submission=user_current_score))
            
            # Create FlagSubmission entries
            db.session.refresh(challenge)
            for flag in challenge.flags:
                flag_submissions_to_add.append(FlagSubmission(user_id=user.id, challenge_id=challenge.id, challenge_flag_id=flag.id, timestamp=submission_time))
                flag_attempts_to_add.append(FlagAttempt(user_id=user.id, challenge_id=challenge.id, submitted_flag=flag.flag_content, is_correct=True, timestamp=submission_time))

    db.session.add_all(submissions_to_add)
    db.session.add_all(flag_submissions_to_add)
    db.session.commit()

    # Generate some failed attempts (general purpose, not tied to specific stripes)
    # The existing failed attempt logic should work fine without specific modifications here.
    # No changes needed for failed attempt generation for stripe demonstration.
    
    # Recalculate and update user scores based on actual submissions for all users
    for user in users:
        user.score = sum(s.challenge_rel.points for s in Submission.query.filter_by(user_id=user.id).all())
    db.session.commit()

    # Set some users to hidden (existing logic)
    users[0].hidden = True
    users[1].hidden = True
    db.session.commit()

    # Add settings (existing logic)
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