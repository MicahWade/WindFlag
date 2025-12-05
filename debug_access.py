
import os
import sys
from app import create_app
from scripts.models import User, Challenge, Category, ApiKey, Submission
from flask import g
import hashlib
import urllib.parse # Import urllib.parse for URL parsing

# Create the Flask app context
app = create_app()

def check_access():
    with app.app_context():
        print("\n--- WindFlag Debug Access Tool ---")
        
        username = ""
        api_key_input = ""
        category_input = ""
        challenge_input = ""

        # Option to paste full URL
        full_url_input = input("Enter Full Challenge URL (e.g., http://host:port/Category/Challenge?api_key=xyz) or press Enter for manual input: ").strip()

        if full_url_input:
            parsed_url = urllib.parse.urlparse(full_url_input)
            path_parts = parsed_url.path.strip("/").split("/")
            query_params = urllib.parse.parse_qs(parsed_url.query)

            if len(path_parts) >= 2:
                category_input = path_parts[0]
                challenge_input = path_parts[1]
            
            if 'api_key' in query_params:
                api_key_input = query_params['api_key'][0]
            
            # For username, we assume the user will enter it based on the API key or later for verification
            print("\n--- Parsed from URL ---")
            print(f" Category: {category_input}")
            print(f" Challenge: {challenge_input}")
            print(f" API Key (from URL): {api_key_input[:8]}..." if api_key_input else " Not found")
            print("-----------------------")

            username = input("Enter your Username (required for user context): ").strip()

        else: # Manual Input Fallback
            username = input("Enter your Username: ").strip()
            print("\n[Optional] Paste the API Key you are using to verify it matches this user.")
            api_key_input = input("API Key (press Enter to skip): ").strip()
            print("\nEnter the Category and Challenge name exactly as seen in the UI or URL (underscores are handled).")
            category_input = input("Category Name (e.g., 'Linux Basics' or 'Linux_Basics'): ").strip()
            challenge_input = input("Challenge Name (e.g., 'Cat the Flag' or 'Cat_the_Flag'): ").strip()
        
        # 1. Get User
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"Error: User '{username}' not found.")
            return

        print(f"User Found: {user.username} (ID: {user.id})")
        print(f" - Is Admin: {user.is_admin}")
        print(f" - Is Hidden: {user.hidden}")

        # 2. Check API Key (Optional verification)
        if api_key_input:
            key_hash = hashlib.sha256(api_key_input.encode('utf-8')).hexdigest()
            api_key_entry = ApiKey.query.filter_by(key_hash=key_hash, is_active=True).first()
            if api_key_entry:
                 if api_key_entry.user_id == user.id:
                     print(" -> API Key Check: VALID and belongs to this user.")
                 else:
                     other_user = User.query.get(api_key_entry.user_id)
                     print(f" -> API Key Check: WARNING! Valid key, but belongs to user '{other_user.username}' (ID: {other_user.id}).")
            else:
                print(" -> API Key Check: INVALID or inactive.")
        
        # 3. Find Category (Handle underscores and case)
        category = Category.query.filter_by(name=category_input).first()
        if not category:
            # Try replacing underscores
            category = Category.query.filter_by(name=category_input.replace('_', ' ')).first()
        if not category:
            # Try case insensitive
            category = Category.query.filter(Category.name.ilike(category_input.replace('_', ' '))).first()

        if not category:
            print(f"\nError: Category '{category_input}' NOT found.")
            print("Available Categories:")
            for c in Category.query.all():
                print(f" - {c.name}")
            return

        # 4. Find Challenge (Handle underscores and case)
        challenge = Challenge.query.filter_by(name=challenge_input, category_id=category.id).first()
        if not challenge:
            challenge = Challenge.query.filter_by(name=challenge_input.replace('_', ' '), category_id=category.id).first()
        if not challenge:
            challenge = Category.query.filter(Challenge.name.ilike(challenge_input.replace('_', ' ')), Challenge.category_id == category.id).first()
            
        if not challenge:
            print(f"\nError: Challenge '{challenge_input}' NOT found in category '{category.name}'.")
            
            print(f"Available Challenges in '{category.name}':")
            for c in category.challenges:
                print(f" - {c.name}")
            return

        print(f"\nChecking Access for: [{category.name}] / [{challenge.name}]")
        print(f" - Challenge ID: {challenge.id}")
        print(f" - Hidden: {challenge.is_hidden}")
        print(f" - Category Hidden: {category.is_hidden}")
        print(f" - Unlock Type: {challenge.unlock_type}")

        # 5. Check Logic
        solved_challenges = {sub.challenge_id for sub in user.submissions}
        user_completed_challenges_cache = {user.id: solved_challenges}
        
        print(f"\nUser '{user.username}' has solved {len(solved_challenges)} challenges.")
        if solved_challenges:
            print(" Solved Challenge IDs:", solved_challenges)

        is_unlocked = challenge.is_unlocked_for_user(user, user_completed_challenges_cache)
        print(f"\n>>> IS UNLOCKED: {is_unlocked} <<<")
        
        if not is_unlocked:
            print("\n--- REASON FOR LOCK ---")
            if user.is_admin:
                print(" [!] User is Admin. Admins should always have access. This is unexpected.")
            
            if challenge.is_hidden:
                print(" [x] Challenge is marked as HIDDEN.")
            
            if category.is_hidden:
                print(" [x] Category is marked as HIDDEN.")
            
            # Check Prerequisites
            if challenge.prerequisite_challenge_ids:
                req_ids = set(challenge.prerequisite_challenge_ids)
                completed = solved_challenges
                missing = req_ids - completed
                if missing:
                    print(f" [x] Missing Prerequisite Challenges (IDs: {missing})")
                    for mid in missing:
                        mc = Challenge.query.get(mid)
                        print(f"     - MISSING: {mc.name} (ID: {mc.id})")
                else:
                    print(" [v] Specific challenge prerequisites met.")
            
            if challenge.unlock_type == 'PREREQUISITE_PERCENTAGE':
                total = Challenge.query.count()
                done = len(solved_challenges)
                pct = (done/total)*100 if total else 0
                req_pct = challenge.prerequisite_percentage_value
                if pct < req_pct:
                     print(f" [x] Completion Percentage too low: {pct:.2f}% (Required: {req_pct}%)")

            if challenge.unlock_type == 'PREREQUISITE_COUNT':
                count = len(solved_challenges)
                req_count = challenge.prerequisite_count_value
                if count < req_count:
                    print(f" [x] Not enough challenges solved: {count} (Required: {req_count})")

            if challenge.unlock_type == 'TIMED':
                 from scripts.utils import make_datetime_timezone_aware
                 from datetime import datetime, UTC
                 if challenge.unlock_date_time:
                     aware_dt = make_datetime_timezone_aware(challenge.unlock_date_time)
                     if datetime.now(UTC) < aware_dt:
                         print(f" [x] Time locked until: {aware_dt}")

if __name__ == "__main__":
    check_access()

