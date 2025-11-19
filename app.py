from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from scripts.config import Config
from scripts.forms import RegistrationForm, LoginForm, FlagSubmissionForm, InlineGiveAwardForm # Import forms
from datetime import datetime, UTC, timedelta # Import datetime, UTC, and timedelta
from sqlalchemy import func # Import func for aggregation
from sqlalchemy.orm import joinedload # Import joinedload for eager loading
from scripts.extensions import db, login_manager, bcrypt, get_setting # Import extensions and get_setting
from scripts.admin_routes import admin_bp # Import admin blueprint
import sys # Import sys
import argparse # Import argparse
import threading # Import threading
import os # Import os
import json # Import json
import yaml # Import yaml
import os # Import os

import os # Import os
from dotenv import load_dotenv # Import load_dotenv

def create_app(config_class=Config):
    app = Flask(__name__)
    # Load environment variables from .env file in the project root
    load_dotenv(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), '.env'))
    app.config.from_object(config_class)
    app.config['APP_NAME'] = os.getenv('APP_NAME', 'WindFlag') # Add this line
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.unauthorized_handler(lambda: redirect(url_for('home')))
    bcrypt.init_app(app)

    from scripts.models import User, Category, Challenge, Submission, ChallengeFlag, FlagSubmission, Award, AwardCategory, FlagAttempt # Import FlagAttempt

    app.register_blueprint(admin_bp) # Register admin blueprint

    @app.context_processor
    def inject_global_config():
        return dict(disable_signup=app.config['DISABLE_SIGNUP'])

    @app.route('/')
    @app.route('/home')
    def home():
        if current_user.is_authenticated:
            return redirect(url_for('profile'))
        return render_template("index.html")

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if app.config['DISABLE_SIGNUP']:
            flash('User registration is currently disabled.', 'info')
            return redirect(url_for('home'))
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        # Pass app.config to the RegistrationForm to allow dynamic field validation
        form = RegistrationForm(app.config)
        if form.validate_on_submit():
            # Check join code if required
            if app.config['REQUIRE_JOIN_CODE'] and form.join_code.data != app.config['JOIN_CODE']:
                flash('Invalid join code.', 'danger')
                return render_template('register.html', title='Register', form=form,
                                       require_email=app.config['REQUIRE_EMAIL'],
                                       require_join_code=app.config['REQUIRE_JOIN_CODE'])
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            # Conditionally set email data based on REQUIRE_EMAIL config
            email_data = form.email.data if app.config['REQUIRE_EMAIL'] else None
            user = User(username=form.username.data, email=email_data, password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        # Pass configuration flags to the template for conditional rendering of fields
        return render_template('register.html', title='Register', form=form,
                               require_email=app.config['REQUIRE_EMAIL'],
                               require_join_code=app.config['REQUIRE_JOIN_CODE'])

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
        return render_template('login.html', title='Login', form=form)

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route('/profile')
    @login_required
    def profile():
        return user_profile(current_user.username) # Call the user_profile function with current_user's username

    @app.route('/profile/<username>')
    @login_required
    def user_profile(username):
        # Start building the query for target_user
        user_query = User.query.filter_by(username=username)

        # If current user is admin, eager load awards received and given
        if current_user.is_admin:
            user_query = user_query.options(
                joinedload(User.awards_received).joinedload(Award.category),
                joinedload(User.awards_received).joinedload(Award.giver)
            )
        
        target_user = user_query.first_or_404()

        # Access control: If user is hidden and current user is not admin, deny access
        if target_user.hidden and not current_user.is_admin:
            flash('You do not have permission to view this profile.', 'danger')
            return redirect(url_for('home')) # Or abort(403)

        # Calculate user rank
        # This query gets all non-hidden users, orders them by score, and assigns a rank
        ranked_users = db.session.query(
            User.id,
            User.username,
            User.score,
            func.rank().over(order_by=User.score.desc()).label('rank')
        ).filter(User.hidden == False).subquery()

        user_rank_data = db.session.query(ranked_users.c.rank)\
                                   .filter(ranked_users.c.id == target_user.id)\
                                   .first()
        user_rank = user_rank_data.rank if user_rank_data else None

        # Fetch submissions for the target user, eager-loading challenge and category details
        user_submissions = Submission.query.filter_by(user_id=target_user.id)\
                                           .options(joinedload(Submission.challenge_rel).joinedload(Challenge.category))\
                                           .order_by(Submission.timestamp.desc())\
                                           .all()

        # Initialize InlineGiveAwardForm
        give_award_form = None
        if current_user.is_admin:
            give_award_form = InlineGiveAwardForm()
            give_award_form.category.choices = [(ac.id, ac.name) for ac in AwardCategory.query.order_by(AwardCategory.name).all()]

        return render_template('profile.html', title=f"{target_user.username}'s Profile",
                               user=target_user, submissions=user_submissions, user_rank=user_rank,
                               give_award_form=give_award_form)

    @app.route('/challenges')
    @login_required
    def challenges():
        flag_form = FlagSubmissionForm()
        categories = Category.query.options(joinedload(Category.challenges).joinedload(Challenge.flags)).all()

        # Get all challenge IDs completed by the current user
        completed_challenge_ids = {s.challenge_id for s in Submission.query.filter_by(user_id=current_user.id).all()}

        # Get all flags submitted by the current user
        submitted_flag_ids = {fs.challenge_flag_id for fs in FlagSubmission.query.filter_by(user_id=current_user.id).all()}

        # Add is_completed and submitted_flags_count attribute to each challenge
        for category in categories:
            for challenge in category.challenges:
                challenge.is_completed = challenge.id in completed_challenge_ids
                
                # Count how many flags the user has submitted for this specific challenge
                challenge.submitted_flags_count = FlagSubmission.query.filter_by(
                    user_id=current_user.id,
                    challenge_id=challenge.id
                ).count()
                
                # Determine total flags for the challenge
                challenge.total_flags = len(challenge.flags)

        return render_template('challenges.html', title='Challenges', categories=categories, flag_form=flag_form)

    @app.route('/submit_flag/<int:challenge_id>', methods=['POST'])
    @login_required
    def submit_flag(challenge_id):
        form = FlagSubmissionForm()
        if form.validate_on_submit():
            challenge = Challenge.query.options(joinedload(Challenge.flags)).get_or_404(challenge_id)

            # 1. Check if challenge is already fully solved
            if Submission.query.filter_by(user_id=current_user.id, challenge_id=challenge.id).first():
                # Record the attempt even if already solved
                new_flag_attempt = FlagAttempt(
                    user_id=current_user.id,
                    challenge_id=challenge.id,
                    submitted_flag=form.flag.data,
                    is_correct=False, # Assume incorrect for already solved challenges
                    timestamp=datetime.now(UTC)
                )
                db.session.add(new_flag_attempt)
                db.session.commit()
                return jsonify({'success': False, 'message': 'You have already solved this challenge!'})

            submitted_flag_content = form.flag.data
            correct_flag_found = None # Will store the matching ChallengeFlag object

            # 2. Find if the submitted flag matches any of the challenge's flags
            for cf in challenge.flags:
                if challenge.case_sensitive:
                    if cf.flag_content == submitted_flag_content:
                        correct_flag_found = cf
                        break
                else:
                    if cf.flag_content.lower() == submitted_flag_content.lower():
                        correct_flag_found = cf
                        break
            
            # Record the attempt in FlagAttempt table
            new_flag_attempt = FlagAttempt(
                user_id=current_user.id,
                challenge_id=challenge.id,
                submitted_flag=submitted_flag_content,
                is_correct=(correct_flag_found is not None),
                timestamp=datetime.now(UTC)
            )
            db.session.add(new_flag_attempt)
            db.session.commit() # Commit the attempt immediately

            if correct_flag_found:
                # 3. Check if this specific flag has already been submitted by the user (correctly)
                if FlagSubmission.query.filter_by(user_id=current_user.id, challenge_flag_id=correct_flag_found.id).first():
                    return jsonify({'success': False, 'message': 'You have already submitted this specific flag.'})
                
                # 4. Record the new flag submission in FlagSubmission table
                new_flag_submission = FlagSubmission(
                    user_id=current_user.id,
                    challenge_id=challenge.id,
                    challenge_flag_id=correct_flag_found.id,
                    timestamp=datetime.now(UTC)
                )
                db.session.add(new_flag_submission)
                db.session.commit() # Commit to ensure the new flag submission is in the DB for counting

                # 5. Re-evaluate if the challenge is now fully solved
                is_challenge_solved = False
                user_submitted_flags_for_challenge = FlagSubmission.query.filter_by(
                    user_id=current_user.id,
                    challenge_id=challenge.id
                ).count()
                
                total_flags_for_challenge = len(challenge.flags)

                if challenge.multi_flag_type == 'SINGLE' or challenge.multi_flag_type == 'ANY':
                    is_challenge_solved = True # Any one correct flag solves it
                elif challenge.multi_flag_type == 'ALL':
                    if user_submitted_flags_for_challenge == total_flags_for_challenge:
                        is_challenge_solved = True
                elif challenge.multi_flag_type == 'N_OF_M':
                    if challenge.multi_flag_threshold and user_submitted_flags_for_challenge >= challenge.multi_flag_threshold:
                        is_challenge_solved = True
                
                if is_challenge_solved:
                    # 6. Mark challenge as solved in Submission table
                    new_submission = Submission(user_id=current_user.id, challenge_id=challenge.id, timestamp=datetime.now(UTC))
                    db.session.add(new_submission)
                    current_user.score += challenge.points # Update user score
                    new_submission.score_at_submission = current_user.score # Record score at this submission
                    db.session.commit()
                    return jsonify({'success': True, 'message': f'Correct Flag! Challenge Solved! You earned {challenge.points} points!'})
                else:
                    # 7. Flag was correct, but challenge not fully solved yet
                    return jsonify({
                        'success': True,
                        'message': f'Correct Flag! You have submitted {user_submitted_flags_for_challenge} of {total_flags_for_challenge} flags for this challenge.'
                    })
            else:
                # 8. Incorrect Flag
                return jsonify({'success': False, 'message': 'Incorrect Flag. Please try again.'})
        return jsonify({'success': False, 'message': 'Invalid form submission.'})

    @app.route('/api/scoreboard_data')
    @login_required
    def scoreboard_data():
        try:
            top_x = int(get_setting('TOP_X_SCOREBOARD', '10'))

            # 1. all_players_ranked data (for the table)
            all_players_ranked_query = db.session.query(
                User.username,
                func.coalesce(func.sum(Challenge.points), 0).label('score'),
                func.max(Submission.timestamp).label('last_submission')
            ).outerjoin(Submission, User.id == Submission.user_id)\
             .outerjoin(Challenge, Submission.challenge_id == Challenge.id)\
             .filter(User.hidden == False)\
             .group_by(User.id, User.username)\
             .order_by(func.coalesce(func.sum(Challenge.points), 0).desc(), func.max(Submission.timestamp).asc())\
             .all()
            
            all_players_ranked = []
            for user_data in all_players_ranked_query:
                all_players_ranked.append({
                    'username': user_data.username,
                    'score': user_data.score,
                })

            # 2. top_players_history data (for the graph)
            # Get the top_x users based on current score
            top_users_query = db.session.query(User)\
                                        .filter(User.hidden == False)\
                                        .order_by(User.score.desc())\
                                        .limit(top_x)\
                                        .all()
            
            top_players_history = {} # New structure: { 'username': [{'x': timestamp, 'y': score}, ...] }
            
            for user in top_users_query:
                user_history_list = []
                # Get all submissions for the current user, ordered by timestamp
                user_submissions = Submission.query.filter_by(user_id=user.id).order_by(Submission.timestamp.asc()).all()

                # Add an initial 0 score point
                if user_submissions:
                    # Initial 0 score point, slightly before the first submission
                    initial_timestamp = user_submissions[0].timestamp - timedelta(microseconds=1)
                    user_history_list.append({'x': initial_timestamp.isoformat(), 'y': 0})
                else:
                    # If no submissions, just a single 0 score point at current time
                    user_history_list.append({'x': datetime.now(UTC).isoformat(), 'y': 0})

                # Add all actual submission points
                for submission in user_submissions:
                    user_history_list.append({'x': submission.timestamp.isoformat(), 'y': submission.score_at_submission})
                
                top_players_history[user.username] = user_history_list

            graph_type = get_setting('SCOREBOARD_GRAPH_TYPE', 'line') # Get graph type setting

            return jsonify({
                'top_players_history': top_players_history, # Now a dictionary of lists
                'all_players_ranked': all_players_ranked,
                'graph_type': graph_type # Include graph type in the response
            })
        except Exception as e:
            current_app.logger.error(f"Error fetching scoreboard data: {e}")
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    @app.route('/api/challenge/<int:challenge_id>/solvers')
    @login_required
    def get_challenge_solvers(challenge_id):
        challenge = Challenge.query.get_or_404(challenge_id)
        submissions = Submission.query.filter_by(challenge_id=challenge.id).all()
        solvers = [submission.solver.username for submission in submissions]
        return jsonify({'solvers': solvers, 'solver_count': len(solvers)})

    @app.route('/scoreboard')
    @login_required
    def scoreboard():
        return render_template('scoreboard.html', title='Scoreboard')

    return app

def export_data_to_yaml(output_file_path, data_type='all'):
    with create_app().app_context():
        from scripts.models import User, Category, Challenge, ChallengeFlag, Submission, FlagSubmission, FlagAttempt, AwardCategory, Award
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
                    # Password hash is not exported for security reasons
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
                challenges_data.append({
                    'name': challenge.name,
                    'description': challenge.description,
                    'points': challenge.points,
                    'category': challenge.category.name,
                    'case_sensitive': challenge.case_sensitive,
                    'multi_flag_type': challenge.multi_flag_type,
                    'multi_flag_threshold': challenge.multi_flag_threshold,
                    'flags': flags_data
                })
            exported_data['challenges'] = challenges_data
        
        # Export other data types if needed (e.g., submissions, flag_attempts, awards)
        # For 'all', we might want to include everything, but for now, let's stick to core entities.
        # Submissions, FlagSubmissions, FlagAttempts, Awards are usually tied to specific user/challenge IDs
        # and might be complex to re-import without careful ID management.
        # For a simple export, we can just list them.

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

def import_users_from_json(json_file_path):
    with create_app().app_context():
        from scripts.models import User
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

def import_challenges_from_yaml(yaml_file_path):
    with create_app().app_context():
        from scripts.models import Category, Challenge, ChallengeFlag
        try:
            with open(yaml_file_path, 'r') as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Error: YAML file not found at {yaml_file_path}")
            return
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            return

        if 'challenges' not in data:
            print("Error: YAML file must contain a 'challenges' key.")
            return

        for challenge_data in data['challenges']:
            # Get or create category
            category_name = challenge_data.get('category', 'Uncategorized')
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name)
                db.session.add(category)
                db.session.commit() # Commit to get category ID

            # Create challenge
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
                multi_flag_threshold=challenge_data.get('multi_flag_threshold')
            )
            db.session.add(challenge)
            db.session.commit() # Commit to get challenge ID

            # Add flags
            flags = challenge_data.get('flags', [])
            if not flags:
                print(f"Warning: Challenge '{challenge_name}' has no flags defined.")
            for flag_content in flags:
                challenge_flag = ChallengeFlag(challenge_id=challenge.id, flag_content=flag_content)
                db.session.add(challenge_flag)
            db.session.commit()
            print(f"Challenge '{challenge_name}' imported successfully.")
        print("Challenge import process completed.")

def create_admin(username, password):
    with create_app().app_context():
        from scripts.models import User
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        admin = User(username=username, email=None, password_hash=hashed_password, is_admin=True, is_super_admin=True, hidden=True)
        db.session.add(admin)
        db.session.commit()
        print(f"Super Admin user with username {username} created successfully.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='WindFlag CTF Platform', add_help=False)
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                        help='Show this help message and exit.')
    parser.add_argument('-admin', nargs=2, metavar=('USERNAME', 'PASSWORD'), help='Create an admin user')
    parser.add_argument('-admin-r', type=str, metavar='USERNAME', help='Remove a super admin user. Only super admins can be removed this way.')
    parser.add_argument('-yaml', '-y', type=str, metavar='YAML_FILE', help='Import challenges from a YAML file.')
    parser.add_argument('-users', '-u', type=str, metavar='JSON_FILE', help='Import users from a JSON file.') # New argument
    parser.add_argument('-export-yaml', '-e', nargs='+', metavar=('OUTPUT_FILE', 'DATA_TYPE'), help='Export data to a YAML file. Specify "all", "users", "challenges", "categories", "submissions", "flag_attempts", or "awards".')
    parser.add_argument('-test', nargs='?', type=int, const=1800, help='Run the server in test mode with an optional timeout in seconds (default: 1800)')
    args = parser.parse_args()

    # Determine which config to use
    if args.test is not None or '-playwright' in sys.argv:
        from scripts.config import TestConfig
        app = create_app(config_class=TestConfig)
        if '-playwright' in sys.argv:
            test_mode_timeout = 360
        else:
            test_mode_timeout = args.test
    else:
        app = create_app()
        test_mode_timeout = None

    # Check if the database file exists, if not, create it
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all()
            print(f"Database '{db_path}' created successfully.")

    if args.admin:
        create_admin(args.admin[0], args.admin[1])
    elif args.admin_r:
        with app.app_context():
            from scripts.models import User
            user_to_remove = User.query.filter_by(username=args.admin_r).first()
            if user_to_remove:
                if user_to_remove.is_super_admin:
                    db.session.delete(user_to_remove)
                    db.session.commit()
                    print(f"Super Admin user {args.admin_r} removed successfully.")
                else:
                    print(f"Error: User {args.admin_r} is not a Super Admin. Only Super Admins can be removed this way.")
            else:
                print(f"Error: User {args.admin_r} not found.")
    elif args.yaml:
        import_challenges_from_yaml(args.yaml)
    elif args.users: # New conditional for JSON user import
        import_users_from_json(args.users)
    elif args.export_yaml:
        output_file = args.export_yaml[0]
        data_type = 'all'
        if len(args.export_yaml) > 1:
            data_type = args.export_yaml[1]
        export_data_to_yaml(output_file, data_type)
    else:
        # Otherwise, run the Flask app
        if args.test is not None:
            print(f"Running in test mode: server will shut down in {test_mode_timeout} seconds.")
            timer = threading.Timer(test_mode_timeout, os._exit, args=[0])
            timer.start()
        app.run(debug=True, host='0.0.0.0', port=5000)
