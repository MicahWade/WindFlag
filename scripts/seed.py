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
    from flask import current_app # Import current_app inside the function where context is active
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
    test_admin = User(username="test", email="test@example.com", password_hash=test_admin_password, is_admin=True, is_super_admin=True, hidden=True, score=0)

    db.session.add_all([admin1, admin2, test_admin])
    db.session.commit()

    # Generate API keys for admin users if the feature is enabled
    if current_app.config.get('GENERATE_API_KEY_ON_REGISTER', False):
        admin1.generate_new_api_key()
        admin2.generate_new_api_key()
        test_admin.generate_new_api_key()
        db.session.commit() # Commit after generating keys

    # Create users from the generated usernames
    from scripts.utils import generate_usernames
    from flask import current_app
    
    users = []
    
    # Generate preset usernames only if the feature is enabled
    if current_app.config.get('PRESET_USERNAMES_ENABLED', False):
        generated_usernames = generate_usernames(num_to_generate=10) # 10 users for seeding
        user_password = bcrypt.generate_password_hash("userpass").decode('utf-8')

        for i, username in enumerate(generated_usernames):
            user = User(username=username, email=f"{username}_{i}@example.com", password_hash=user_password, is_admin=False, hidden=False, score=0)
            users.append(user)
    
    # Add specific user "zen" as a non-admin user
    zen_password = bcrypt.generate_password_hash("zen").decode('utf-8')
    zen_user = User(username="zen", email="zen@example.com", password_hash=zen_password, is_admin=False, hidden=False, score=0)
    users.append(zen_user)

    db.session.add_all(users)
    db.session.commit()

    # Generate API keys for regular users if the feature is enabled
    if current_app.config.get('GENERATE_API_KEY_ON_REGISTER', False):
        for user in users:
            user.generate_new_api_key()
        db.session.commit() # Commit after generating keys

    # Set some users to hidden immediately after creation
    # This ensures that eligible_users_for_seeding considers these users as hidden from the start
    if len(users) > 0:
        users[0].hidden = True
    if len(users) > 1:
        users[1].hidden = True
    db.session.commit()

    # Create 20 Challenges across a few categories
    categories = []
    for i in range(1, 6): # 5 categories
        category = Category(name=f"Category {i}")
        categories.append(category)
    
    # Add a new hidden category
    hidden_category = Category(name="Hidden Category", is_hidden=True, unlock_type='HIDDEN')
    categories.append(hidden_category)

    # Add a new coding category
    coding_category = Category(name="Coding")
    categories.append(coding_category)

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

    # --- Create a TIMED Challenge (Red Stripe - locked by time) ---
    timed_challenge = Challenge(name="Timed Challenge (Red)", description="This challenge will be available in the future.",
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

    # --- Explicit Challenges for Stripes ---
    # Red Stripe (Locked by Prerequisite Count - unachievable with demo data)
    red_stripe_prereq_challenge = Challenge(name="Red Stripe (Prereq Locked)", description="Requires 99 challenges from Category 1 to unlock.",
                                            points=50, category_id=categories[0].id,
                                            unlock_type='PREREQUISITE_COUNT', prerequisite_count_value=99,
                                            prerequisite_count_category_ids=[categories[0].id])
    challenges.append(red_stripe_prereq_challenge)
    db.session.add(red_stripe_prereq_challenge)

    # Orange Stripe (Unlockable - No Solves) - Will be given 0 submissions later
    orange_stripe_no_solves = Challenge(name="Orange Stripe (No Solves)", description="This challenge should have no solves.",
                                        points=75, category_id=categories[1].id)
    challenges.append(orange_stripe_no_solves)
    db.session.add(orange_stripe_no_solves)
    db.session.commit() # Commit here to ensure IDs are generated

    # Yellow Prerequisite Challenge (solved by ~25% of users)
    yellow_prereq_challenge = Challenge(name="Yellow Prereq", description="Prerequisite for Yellow Stripe.",
                                       points=10, category_id=categories[4].id) # Using a new category
    challenges.append(yellow_prereq_challenge)
    db.session.add(yellow_prereq_challenge)

    # Blue Prerequisite Challenge (solved by ~65% of users)
    blue_prereq_challenge = Challenge(name="Blue Prereq", description="Prerequisite for Blue Stripe.",
                                      points=10, category_id=categories[4].id) # Using same new category
    challenges.append(blue_prereq_challenge)
    db.session.add(blue_prereq_challenge)
    db.session.commit() # Commit here to ensure IDs are generated

    # Yellow Stripe (Unlocked 0-50% Solves) - Now dependent on yellow_prereq_challenge
    yellow_stripe_low_solves = Challenge(name="Yellow Stripe (Low Solves)", description="This challenge should have 0-50% unlocked.",
                                         points=120, category_id=categories[2].id,
                                         unlock_type='PREREQUISITE_CHALLENGES',
                                         prerequisite_challenge_ids=[yellow_prereq_challenge.id])
    challenges.append(yellow_stripe_low_solves)
    db.session.add(yellow_stripe_low_solves)

    # Blue Stripe (Rarely Unlocked 50-90% Solves) - Now dependent on blue_prereq_challenge
    blue_stripe_medium_solves = Challenge(name="Blue Stripe (Medium Solves)", description="This challenge should have 50-90% unlocked.",
                                          points=150, category_id=categories[3].id,
                                          unlock_type='PREREQUISITE_CHALLENGES',
                                          prerequisite_challenge_ids=[blue_prereq_challenge.id])
    challenges.append(blue_stripe_medium_solves)
    db.session.add(blue_stripe_medium_solves)
    
    # Hidden Category Challenge (Red Stripe if hidden and no solves)
    hidden_category_challenge = Challenge(name="Hidden Cat Challenge", description="Challenge in a hidden category.",
                                          points=80, category_id=hidden_category.id, is_hidden=True)
    challenges.append(hidden_category_challenge)
    db.session.add(hidden_category_challenge)

    # --- CODING CHALLENGES ---
    python_coding_challenge = Challenge(name="Python: Hello World",
                                        description="Write a Python program that prints 'Hello, Python!'",
                                        points=50, category_id=coding_category.id,
                                        challenge_type='CODING', language='python3',
                                        expected_output='Hello, Python!',
                                        setup_code=None, test_case_input=None,
                                        starter_code="") # Removed starter_code content
    challenges.append(python_coding_challenge)
    db.session.add(python_coding_challenge)

    nodejs_coding_challenge = Challenge(name="Node.js: Simple Sum",
                                        description="Write a Node.js program that reads two numbers from stdin and prints their sum. For example, if input is '3\\n5', output should be '8'.",
                                        points=75, category_id=coding_category.id,
                                        challenge_type='CODING', language='nodejs',
                                        expected_output='8',
                                        setup_code=None, test_case_input='3\n5',
                                        starter_code="") # Removed starter_code content
    challenges.append(nodejs_coding_challenge)
    db.session.add(nodejs_coding_challenge)

    php_coding_challenge = Challenge(name="PHP: Echo Name",
                                     description="Write a PHP program that reads a name from stdin and prints 'Hello, [name]!' For example, if input is 'World', output should be 'Hello, World!'.",
                                     points=60, category_id=coding_category.id,
                                     challenge_type='CODING', language='php',
                                     expected_output='Hello, World!',
                                     setup_code=None, test_case_input='World',
                                     starter_code="") # Removed starter_code content
    challenges.append(php_coding_challenge)
    db.session.add(php_coding_challenge)

    bash_coding_challenge = Challenge(name="Bash: Grep Log",
                                      description="Write a Bash script that takes a word as argument and greps it from a provided log file. The log file is at /sandbox/log.txt. Print the matching lines. The script will receive 'Error' as test input.",
                                      points=80, category_id=coding_category.id,
                                      challenge_type='CODING', language='bash',
                                      expected_output='Error line 1\nError line 2',
                                      setup_code='echo "Info line 1\\nError line 1\\nInfo line 2\\nError line 2" > /sandbox/log.txt',
                                      test_case_input='Error',
                                      starter_code="") # Removed starter_code content
    challenges.append(bash_coding_challenge)
    db.session.add(bash_coding_challenge)

    dart_coding_challenge = Challenge(name="Dart: Reverse String",
                                      description="Write a Dart program that reads a string from stdin and prints its reverse. For example, if input is 'hello', output should be 'olleh'.",
                                      points=90, category_id=coding_category.id,
                                      challenge_type='CODING', language='dart',
                                      expected_output='olleh',
                                      setup_code=None, test_case_input='hello',
                                      starter_code="") # Removed starter_code content
    challenges.append(dart_coding_challenge)
    db.session.add(dart_coding_challenge)
    
    for i in range(1, 31): # 30 more challenges
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
        db.session.flush() # Flush to get challenge.id before creating flags

        # Add flags for the challenge (for non-coding, non-dynamic, non-http challenges)
        if challenge.challenge_type == 'FLAG' and challenge.multi_flag_type not in ['DYNAMIC', 'HTTP']:
            for _ in range(num_flags_for_challenge):
                flag_content = f"FLAG{{{challenge.name.replace(' ', '_').upper()}}}"
                challenge_flag = ChallengeFlag(challenge_id=challenge.id, flag_content=flag_content)
                db.session.add(challenge_flag)
    
    db.session.commit()

    # Get specific challenge IDs for easier reference
    orange_id = next(c.id for c in challenges if c.name == "Orange Stripe (No Solves)")
    yellow_id = next(c.id for c in challenges if c.name == "Yellow Stripe (Low Solves)")
    blue_id = next(c.id for c in challenges if c.name == "Blue Stripe (Medium Solves)")
    hidden_cat_id = next(c.id for c in challenges if c.name == "Hidden Cat Challenge")
    yellow_prereq_id = next(c.id for c in challenges if c.name == "Yellow Prereq")
    blue_prereq_id = next(c.id for c in challenges if c.name == "Blue Prereq")

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
    
    # Store user solved challenges and scores
    user_data = {user.id: {'solved_challenges': set(), 'score': 0, 'last_submission_time': start_date} for user in users}
    
    # Filter users for seeding to match eligible users in stripe calculation
    eligible_users_for_seeding = [user for user in users if not user.is_admin and not user.hidden]

    # Exclude challenges that should have 0 solves (Orange Stripe, specific Red Stripes)
    challenges_to_exclude_from_solves = [orange_id, hidden_cat_id] # Add any other challenges that should get 0 solves

    for challenge in challenges:
        if challenge.id in challenges_to_exclude_from_solves or challenge.multi_flag_type in ['DYNAMIC', 'HTTP']:
            continue # Skip submission generation for these

        solve_percentage = 0
        if challenge.id == yellow_prereq_id: # Control solve rate for yellow prerequisite
            solve_percentage = 1.0 / len(eligible_users_for_seeding) # Exactly one user solves this
        elif challenge.id == blue_prereq_id: # Control solve rate for blue prerequisite
            solve_percentage = 0.65
        elif challenge.id == yellow_id:
            solve_percentage = 1.0 
        elif challenge.id == blue_id:
            solve_percentage = 1.0 
        else:
            solve_percentage = random.uniform(0.3, 0.9) # General challenges: 30-90% solves

        # Use eligible_users_for_seeding for sampling solvers
        num_solvers = int(len(eligible_users_for_seeding) * solve_percentage)
        # Ensure num_solvers does not exceed the number of eligible users
        num_solvers = min(num_solvers, len(eligible_users_for_seeding))
        solvers = random.sample(eligible_users_for_seeding, num_solvers)
        
        for user in solvers:
            # Ensure challenge hasn't been solved by this user already
            if challenge.id in user_data[user.id]['solved_challenges']:
                continue

            # Simulate submission time
            time_delta = timedelta(hours=random.randint(1, 48))
            submission_time = user_data[user.id]['last_submission_time'] + time_delta
            user_data[user.id]['last_submission_time'] = submission_time 

            # Add submission
            user_data[user.id]['score'] += challenge.points
            submissions_to_add.append(Submission(user_id=user.id, challenge_id=challenge.id, timestamp=submission_time, score_at_submission=user_data[user.id]['score']))
            user_data[user.id]['solved_challenges'].add(challenge.id)
            
            # Add flag submissions and attempts
            db.session.refresh(challenge) # Refresh to get associated flags
            for flag in challenge.flags:
                flag_submissions_to_add.append(FlagSubmission(user_id=user.id, challenge_id=challenge.id, challenge_flag_id=flag.id, timestamp=submission_time))
                flag_attempts_to_add.append(FlagAttempt(user_id=user.id, challenge_id=challenge.id, submitted_flag=flag.flag_content, is_correct=True, timestamp=submission_time))

            # Generate hints for solved challenges
            for hint in challenge.hints:
                if random.random() < 0.3: # 30% chance to unlock a hint for solvers
                    user_hints_to_add.append(UserHint(user_id=user.id, hint_id=hint.id, timestamp=submission_time - timedelta(minutes=10)))
                    user_data[user.id]['score'] -= hint.cost # Deduct hint cost
    
    # Update user scores in the database
    for user in users:
        user.score = user_data[user.id]['score']

    db.session.add_all(submissions_to_add)
    db.session.add_all(flag_submissions_to_add)
    db.session.add_all(flag_attempts_to_add)
    db.session.add_all(user_hints_to_add)
    db.session.commit()

    # --- Add a specific failed flag attempt ---
    # Pick a random user and a random challenge
    if users and challenges:
        random_user = random.choice(users)
        random_challenge = random.choice(challenges)
        
        # Ensure the random challenge has flags, otherwise pick another or skip
        if not random_challenge.flags:
            # Try to find a challenge with flags
            challenge_with_flags = next((c for c in challenges if c.flags), None)
            if challenge_with_flags:
                random_challenge = challenge_with_flags
            else:
                print("Warning: No challenges with flags found for failed attempt demo data.")
                # If no challenges with flags, skip adding a failed attempt involving flags
                # This could still be useful for coding challenges, but the prompt implies flag attempts.
                pass 

        # Proceed only if a suitable challenge (with flags or coding) is found
        if random_challenge:
            incorrect_flag_content = f"WRONG_FLAG_{random_challenge.id}_BY_{random_user.id}"
            
            # If it's a coding challenge, the "flag" would be the submitted code
            if random_challenge.challenge_type == 'CODING':
                incorrect_flag_content = f"incorrect_code_for_{random_challenge.id}_by_{random_user.id}"

            failed_attempt_time = datetime.now(UTC) - timedelta(minutes=random.randint(1, 60))
            
            failed_flag_attempt = FlagAttempt(
                user_id=random_user.id,
                challenge_id=random_challenge.id,
                submitted_flag=incorrect_flag_content,
                is_correct=False,
                timestamp=failed_attempt_time
            )
            db.session.add(failed_flag_attempt)
            db.session.commit()
            print(f"Added a failed attempt by {random_user.username} for {random_challenge.name} (type: {random_challenge.challenge_type}).")
    # --- End of specific failed flag attempt ---

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