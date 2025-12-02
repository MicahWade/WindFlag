import json
import yaml
from scripts.models import User, Category, Challenge, ChallengeFlag, Hint, Award, Submission, FlagAttempt
from scripts.extensions import db, bcrypt

def export_data_to_yaml(app, output_file_path, data_type='all'):
    with app.app_context():
        exported_data = {}

        if data_type == 'users' or data_type == 'all':
            users = User.query.all()
            users_data = []
            for user in users:
                users_data.append({
                    'username': user.username,
                    'email': user.email,
                    'is_admin': user.is_admin,
                    'is_super_admin': user.is_super_admin,
                    'hidden': user.hidden,
                    'score': user.score
                })
            exported_data['users'] = users_data

        if data_type == 'categories' or data_type == 'all':
            categories = Category.query.all()
            categories_data = []
            for category in categories:
                categories_data.append({
                    'name': category.name
                })
            exported_data['categories'] = categories_data

        if data_type == 'challenges' or data_type == 'all':
            challenges = Challenge.query.all()
            challenges_data = []
            for challenge in challenges:
                flags_data = [flag.flag_content for flag in challenge.flags]
                hints_data = []
                for hint in challenge.hints:
                    hints_data.append({
                        'title': hint.title,
                        'content': hint.content,
                        'cost': hint.cost
                    })
                challenges_data.append({
                    'name': challenge.name,
                    'description': challenge.description,
                    'points': challenge.points,
                    'hint_cost': challenge.hint_cost,
                    'category': challenge.category.name,
                    'case_sensitive': challenge.case_sensitive,
                    'multi_flag_type': challenge.multi_flag_type,
                    'multi_flag_threshold': challenge.multi_flag_threshold,
                    'flags': flags_data,
                    'hints': hints_data
                })
            exported_data['challenges'] = challenges_data
        
        if data_type == 'submissions' or data_type == 'all':
            submissions = Submission.query.all()
            submissions_data = []
            for submission in submissions:
                submissions_data.append({
                    'username': submission.solver.username,
                    'challenge_name': submission.challenge_rel.name,
                    'timestamp': submission.timestamp.isoformat(),
                    'score_at_submission': submission.score_at_submission
                })
            exported_data['submissions'] = submissions_data

        if data_type == 'flag_attempts' or data_type == 'all':
            flag_attempts = FlagAttempt.query.all()
            flag_attempts_data = []
            for attempt in flag_attempts:
                flag_attempts_data.append({
                    'username': attempt.user.username,
                    'challenge_name': attempt.challenge.name,
                    'submitted_flag': attempt.submitted_flag,
                    'is_correct': attempt.is_correct,
                    'timestamp': attempt.timestamp.isoformat()
                })
            exported_data['flag_attempts'] = flag_attempts_data

        if data_type == 'awards' or data_type == 'all':
            awards = Award.query.all()
            awards_data = []
            for award in awards:
                awards_data.append({
                    'recipient_username': award.recipient.username,
                    'category_name': award.category.name,
                    'points_awarded': award.points_awarded,
                    'giver_username': award.giver.username,
                    'timestamp': award.timestamp.isoformat()
                })
            exported_data['awards'] = awards_data

        try:
            with open(output_file_path, 'w') as f:
                yaml.dump(exported_data, f, default_flow_style=False, sort_keys=False)
            print(f"Data of type '{data_type}' exported successfully to {output_file_path}")
        except IOError as e:
            print(f"Error writing to file {output_file_path}: {e}")

def import_users_from_json(app, json_file_path):
    with app.app_context():
        try:
            with open(json_file_path, 'r') as f:
                users_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: JSON file not found at {json_file_path}")
            return
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file: {e}")
            return

        if not isinstance(users_data, list):
            print("Error: JSON file must contain a list of user objects.")
            return

        for user_data in users_data:
            username = user_data.get('username')
            password = user_data.get('password')
            if not username or not password:
                print(f"Skipping user: 'username' and 'password' are required. Data: {user_data}")
                continue

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"Warning: User '{username}' already exists. Skipping import.")
                continue

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(
                username=username,
                email=user_data.get('email'),
                password_hash=hashed_password,
                is_admin=user_data.get('is_admin', False),
                is_super_admin=user_data.get('is_super_admin', False),
                hidden=user_data.get('hidden', False)
            )
            db.session.add(user)
            db.session.commit()
            print(f"User '{username}' imported successfully.")
        print("User import process completed.")

def import_categories_from_yaml(app, yaml_source, is_file=True):
    with app.app_context():
        data = None
        try:
            if is_file:
                with open(yaml_source, 'r') as f:
                    data = yaml.safe_load(f)
            else: # yaml_source is content string
                data = yaml.safe_load(yaml_source)
        except FileNotFoundError:
            print(f"Error: YAML file not found at {yaml_source}")
            return
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            return

        if not data or 'categories' not in data:
            print("Error: YAML source must contain a 'categories' key.")
            return

        categories_to_process_prerequisites = []

        for category_data in data['categories']:
            category_name = category_data.get('name')
            if not category_name:
                print(f"Skipping category: 'name' is required. Data: {category_data}")
                continue

            existing_category = Category.query.filter_by(name=category_name).first()
            if existing_category:
                print(f"Warning: Category '{category_name}' already exists. Skipping import.")
                continue

            category = Category(
                name=category_name,
                unlock_type=category_data.get('unlock_type', 'NONE'),
                prerequisite_percentage_value=category_data.get('prerequisite_percentage_value'),
                prerequisite_count_value=category_data.get('prerequisite_count_value'),
                unlock_date_time=category_data.get('unlock_date_time'),
                is_hidden=category_data.get('is_hidden', False),
                prerequisite_challenge_ids=[],
                prerequisite_count_category_ids=[]
            )
            db.session.add(category)
            db.session.flush()

            categories_to_process_prerequisites.append({
                'category_obj': category,
                'original_data': category_data
            })
            print(f"Category '{category_name}' (Pass 1) imported successfully.")
        
        db.session.commit()

        for item in categories_to_process_prerequisites:
            category_obj = item['category_obj']
            original_data = item['original_data']

            prerequisite_challenge_names = original_data.get('prerequisite_challenge_names', [])
            if prerequisite_challenge_names:
                prerequisite_challenge_ids = []
                for pre_name in prerequisite_challenge_names:
                    pre_challenge = Challenge.query.filter_by(name=pre_name).first()
                    if pre_challenge:
                        prerequisite_challenge_ids.append(pre_challenge.id)
                    else:
                        print(f"Warning: Prerequisite challenge '{pre_name}' for category '{category_obj.name}' not found. Skipping this prerequisite.")
                if prerequisite_challenge_ids:
                    category_obj.prerequisite_challenge_ids = prerequisite_challenge_ids
            
            prerequisite_count_category_names = original_data.get('prerequisite_count_category_names', [])
            if prerequisite_count_category_names:
                prerequisite_count_category_ids = []
                for pre_name in prerequisite_count_category_names:
                    pre_category = Category.query.filter_by(name=pre_name).first()
                    if pre_category:
                        prerequisite_count_category_ids.append(pre_category.id)
                    else:
                        print(f"Warning: Prerequisite category '{pre_name}' for category '{category_obj.name}' not found. Skipping this prerequisite.")
                if prerequisite_count_category_ids:
                    category_obj.prerequisite_count_category_ids = prerequisite_count_category_ids
            
            if prerequisite_challenge_names or prerequisite_count_category_names:
                db.session.add(category_obj)
                db.session.commit()
                print(f"Category '{category_obj.name}' (Pass 2) prerequisites linked successfully.")
        
        print("Category import process completed.")

def import_challenges_from_yaml(app, yaml_source, is_file=True):
    with app.app_context():
        data = None
        try:
            if is_file:
                with open(yaml_source, 'r') as f:
                    data = yaml.safe_load(f)
            else: # yaml_source is content string
                data = yaml.safe_load(yaml_source)
        except FileNotFoundError:
            print(f"Error: YAML file not found at {yaml_source}")
            return
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            return

        challenges_list = []
        if isinstance(data, list):
            challenges_list = data
        elif isinstance(data, dict) and 'challenges' in data:
            challenges_list = data['challenges']
        else:
            print("Error: YAML source must contain a 'challenges' key or be a list of challenges.")
            return

        challenges_to_process_prerequisites = []

        for challenge_data in challenges_list:
            category_name = challenge_data.get('category', 'Uncategorized')
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                print(f"Creating new category: '{category_name}'")
                category = Category(name=category_name)
                db.session.add(category)
                db.session.commit()
            else:
                print(f"Using existing category: '{category_name}'")

            challenge_name = challenge_data.get('name')
            if not challenge_name:
                print(f"Skipping challenge: 'name' is required. Data: {challenge_data}")
                continue

            existing_challenge = Challenge.query.filter_by(name=challenge_name).first()
            if existing_challenge:
                print(f"Warning: Challenge '{challenge_name}' already exists. Skipping import.")
                continue

            challenge = Challenge(
                name=challenge_name,
                description=challenge_data.get('description', ''),
                points=challenge_data.get('points', 0),
                case_sensitive=challenge_data.get('case_sensitive', True),
                category_id=category.id,
                multi_flag_type=challenge_data.get('multi_flag_type', 'SINGLE'),
                multi_flag_threshold=challenge_data.get('multi_flag_threshold'),
                hint_cost=challenge_data.get('hint_cost', 0),
                unlock_type='ALWAYS_UNLOCKED',
                prerequisite_challenge_ids=[],
                challenge_type=challenge_data.get('challenge_type', 'FLAG'),
                language=challenge_data.get('language'),
                starter_code=challenge_data.get('starter_code'),
                expected_output=challenge_data.get('expected_output'),
                test_case_input=challenge_data.get('test_case_input'),
                setup_code=challenge_data.get('setup_code')
            )
            db.session.add(challenge)
            db.session.flush()

            flags = challenge_data.get('flags', [])
            if not flags:
                print(f"Warning: Challenge '{challenge_name}' has no flags defined.")
            for flag_content in flags:
                challenge_flag = ChallengeFlag(challenge_id=challenge.id, flag_content=flag_content)
                db.session.add(challenge_flag)
            
            hints = challenge_data.get('hints', [])
            for hint_data in hints:
                hint_title = hint_data.get('title', 'Hint')
                hint_content = hint_data.get('content')
                hint_cost = hint_data.get('cost', 0)
                if hint_content:
                    hint = Hint(challenge_id=challenge.id, title=hint_title, content=hint_content, cost=hint_cost)
                    db.session.add(hint)
            
            db.session.commit()

            challenges_to_process_prerequisites.append({
                'challenge_obj': challenge,
                'original_data': challenge_data
            })
            print(f"Challenge '{challenge_name}' (Pass 1) imported successfully.")
        
        for item in challenges_to_process_prerequisites:
            challenge_obj = item['challenge_obj']
            original_data = item['original_data']
            
            prerequisite_names = original_data.get('prerequisites', [])
            if prerequisite_names:
                prerequisite_ids = []
                for pre_name in prerequisite_names:
                    pre_challenge = Challenge.query.filter_by(name=pre_name).first()
                    if pre_challenge:
                        prerequisite_ids.append(pre_challenge.id)
                    else:
                        print(f"Warning: Prerequisite challenge '{pre_name}' for '{challenge_obj.name}' not found. Skipping this prerequisite.")
                
                if prerequisite_ids:
                    challenge_obj.prerequisite_challenge_ids = prerequisite_ids
                    challenge_obj.unlock_type = 'CHALLENGE_SOLVED'
                    db.session.add(challenge_obj)
                    db.session.commit()
                    print(f"Challenge '{challenge_obj.name}' (Pass 2) prerequisites linked successfully.")
        
        print("Challenge import process completed.")
