from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from scripts.config import Config
from scripts.forms import RegistrationForm, LoginForm, FlagSubmissionForm # Import forms
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

import os # Import os
from dotenv import load_dotenv # Import load_dotenv

def create_app(config_class=Config):
    app = Flask(__name__)
    # Load environment variables from .env file in the project root
    load_dotenv(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), '.env'))
    app.config.from_object(config_class)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.unauthorized_handler(lambda: redirect(url_for('home')))
    bcrypt.init_app(app)

    from scripts.models import User, Category, Challenge, Submission # Import models here

    app.register_blueprint(admin_bp) # Register admin blueprint

    if '-playwright' in sys.argv:
        def shutdown_server():
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()

        @app.route('/shutdown', methods=['POST'])
        def shutdown():
            shutdown_server()
            return 'Server shutting down...'

    @app.route('/')
    @app.route('/home')
    def home():
        if current_user.is_authenticated:
            return redirect(url_for('profile'))
        return render_template("index.html")

    @app.route('/register', methods=['GET', 'POST'])
    def register():
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
        # This will be expanded later to show solved challenges
        return render_template('profile.html', title='Profile')

    @app.route('/challenges')
    @login_required
    def challenges():
        flag_form = FlagSubmissionForm()
        categories = Category.query.options(joinedload(Category.challenges)).all()

        # Get all challenge IDs completed by the current user
        completed_challenge_ids = {s.challenge_id for s in Submission.query.filter_by(user_id=current_user.id).all()}

        # Add is_completed attribute to each challenge
        for category in categories:
            for challenge in category.challenges:
                challenge.is_completed = challenge.id in completed_challenge_ids

        return render_template('challenges.html', title='Challenges', categories=categories, flag_form=flag_form)

    @app.route('/submit_flag/<int:challenge_id>', methods=['POST'])
    @login_required
    def submit_flag(challenge_id):
        form = FlagSubmissionForm()
        if form.validate_on_submit():
            challenge = Challenge.query.get_or_404(challenge_id)
            if challenge.flag == form.flag.data:
                # Check if user already solved this challenge
                submission = Submission.query.filter_by(user_id=current_user.id, challenge_id=challenge.id).first()
                if submission:
                    return jsonify({'success': False, 'message': 'You have already solved this challenge!'})
                else:
                    new_submission = Submission(user_id=current_user.id, challenge_id=challenge.id, timestamp=datetime.now(UTC))
                    db.session.add(new_submission)
                    current_user.score += challenge.points # Update user score
                    new_submission.score_at_submission = current_user.score # Record score at this submission
                    db.session.commit()
                    return jsonify({'success': True, 'message': f'Correct Flag! You earned {challenge.points} points!'})
            else:
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

    @app.route('/scoreboard')
    @login_required
    def scoreboard():
        return render_template('scoreboard.html', title='Scoreboard')

    return app

def create_admin(username, password):
    with create_app().app_context():
        from scripts.models import User
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        admin = User(username=username, email=None, password_hash=hashed_password, is_admin=True, hidden=True)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user with username {username} created successfully.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='WindFlag CTF Platform')
    parser.add_argument('-admin', nargs=2, metavar=('USERNAME', 'PASSWORD'), help='Create an admin user')
    parser.add_argument('-test', nargs='?', type=int, const=40, help='Run the server in test mode with an optional timeout in seconds (default: 40)')
    args = parser.parse_args()

    # Determine which config to use
    if args.test is not None:
        from scripts.config import TestConfig
        app = create_app(config_class=TestConfig)
        test_mode_timeout = args.test
    else:
        app = create_app()
        test_mode_timeout = None # Not in test mode, no timeout

    # Check if the database file exists, if not, create it
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all()
            print(f"Database '{db_path}' created successfully.")

    if args.admin:
        # If -admin is used, just create the admin and exit
        create_admin(args.admin[0], args.admin[1])
    else:
        # Otherwise, run the Flask app
        if args.test is not None:
            print(f"Running in test mode: server will shut down in {test_mode_timeout} seconds.")
            timer = threading.Timer(test_mode_timeout, os._exit, args=[0])
            timer.start()
        app.run(debug=True, host='0.0.0.0', port=5000)
