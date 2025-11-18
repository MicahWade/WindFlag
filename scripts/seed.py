from scripts.extensions import db, bcrypt
from scripts.models import User, Category, Challenge, Submission, Setting, ChallengeFlag, FlagSubmission, MULTI_FLAG_TYPES
from datetime import datetime, UTC, timedelta
import random

def seed_database():
    # Clear existing data
    db.session.query(FlagSubmission).delete() # New: Clear FlagSubmission
    db.session.query(Submission).delete()
    db.session.query(ChallengeFlag).delete() # New: Clear ChallengeFlag
    db.session.query(Challenge).delete()
    db.session.query(Category).delete()
    db.session.query(User).delete()
    db.session.query(Setting).delete()
    db.session.commit()

    # Create 2 Admins
    admin_password = bcrypt.generate_password_hash("adminpass").decode('utf-8')
    admin1 = User(username="admin1", email="admin1@example.com", password_hash=admin_password, is_admin=True, hidden=True, score=0)
    admin2 = User(username="admin2", email="admin2@example.com", password_hash=admin_password, is_admin=True, hidden=True, score=0)
    
    # New: Create 'test' admin user
    test_admin_password = bcrypt.generate_password_hash("test").decode('utf-8')
    test_admin = User(username="test", email="test@example.com", password_hash=test_admin_password, is_admin=True, hidden=True, score=0)

    db.session.add_all([admin1, admin2, test_admin]) # Add test_admin
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

        if multi_flag_type == 'SINGLE':
            num_flags_for_challenge = 1
        elif multi_flag_type == 'N_OF_M':
            multi_flag_threshold = random.randint(1, num_flags_for_challenge) # N must be <= M

        challenge = Challenge(name=f"Challenge {i}", description=f"Description for Challenge {i}",
                              points=i * 10, case_sensitive=True, category_id=category_id,
                              multi_flag_type=multi_flag_type, multi_flag_threshold=multi_flag_threshold)
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

    # Make users complete challenges
    all_user_challenge_pairs = []
    for user in users:
        for challenge in challenges:
            all_user_challenge_pairs.append((user, challenge))
    
    random.shuffle(all_user_challenge_pairs) # Randomize the order of completions

    submissions_to_add = []
    flag_submissions_to_add = [] # New list for FlagSubmission
    
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

                # For seeding, assume all flags for a multi-flag challenge are submitted correctly
                # This will create a Submission entry, implying the challenge is solved.
                # We also need to create FlagSubmission entries for each flag of the challenge.
                
                # Temporarily update user score for score_at_submission
                user.score += challenge.points
                submission = Submission(user_id=user.id, challenge_id=challenge.id, timestamp=submission_time, score_at_submission=user.score)
                submissions_to_add.append(submission)
                user_solved_challenges[user.id].add(challenge.id)

                # Create FlagSubmission entries for all flags of this challenge
                # Ensure challenge.flags is loaded
                db.session.refresh(challenge) # Refresh to load flags relationship
                for flag in challenge.flags:
                    flag_submission = FlagSubmission(user_id=user.id, challenge_id=challenge.id,
                                                     challenge_flag_id=flag.id, timestamp=submission_time)
                    flag_submissions_to_add.append(flag_submission)
    
    db.session.add_all(submissions_to_add)
    db.session.add_all(flag_submissions_to_add) # Add new FlagSubmission entries
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
        "admin_ids": [admin1.id, admin2.id, test_admin.id], # Include test_admin.id
        "user_ids": [user.id for user in users],
        "category_ids": [category.id for category in categories],
        "challenge_ids": [challenge.id for challenge in challenges]
    }