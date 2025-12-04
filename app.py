
"""
Main application file for the WindFlag CTF platform.

This file initializes the Flask application, configures extensions, defines
routes for user authentication, profile management, challenge interaction,
and scoreboard display. It also includes utility functions for data export/import
and admin user creation.
"""
import os # Moved to top
from dotenv import load_dotenv # Moved to top
# Load environment variables from .env file in the project root
load_dotenv(os.path.join(os.path.abspath(os.path.dirname(__file__)), '.env')) # Moved to top

from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, current_app, session, make_response
from flask_login import login_user, current_user, logout_user, login_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from scripts.config import Config
from scripts.forms import RegistrationForm, LoginForm, FlagSubmissionForm, InlineGiveAwardForm, PasswordResetForm
from datetime import datetime, UTC, timedelta
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from scripts.extensions import db, login_manager, bcrypt, get_setting
from scripts.admin_routes import admin_bp
from scripts.api_key_routes import api_key_bp # Import api_key_bp
from scripts.api_routes import api_bp # Import api_bp
from flask_restx import Api # Import Api from flask_restx
from scripts.config import Config # Import Config

# ... existing code ...

app = Flask(__name__)
app.config.from_object(Config) # Load configuration

from scripts.theme_utils import get_active_theme # New: Import theme_utils

from scripts.chart_data_utils import get_profile_points_over_time_data, get_profile_fails_vs_succeeds_data, get_profile_categories_per_score_data, get_profile_challenges_complete_data, get_global_score_history_data
import sys
import argparse
import threading
import os
import json
import yaml
from dotenv import load_dotenv
from scripts.utils import make_datetime_timezone_aware, generate_usernames # New: For timezone handling and preset usernames


def create_app(config_class=Config):
    """
    Initializes and configures the Flask application.

    Args:
        config_class: The configuration class to use for the Flask app.
                      Defaults to `Config`.

    Returns:
        A Flask application instance.
    """
    app = Flask(__name__)
    # Load environment variables from .env file in the project root
    load_dotenv(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), '.env'))
    app.config.from_object(config_class)
    app.config['APP_NAME'] = os.getenv('APP_NAME', 'WindFlag')
    print(f"DEBUG: ENABLE_SWITCHBOARD is set to: {app.config.get('ENABLE_SWITCHBOARD')}")
    
    
    # Initialize extensions with the app instance *before* entering app context
    # if those extensions are used within that context.
    db.init_app(app)
    print(f"INFO: Database configured: {app.config['SQLALCHEMY_DATABASE_URI']}") # Added line

    # New check for PostgreSQL configuration
    if app.config.get('USE_POSTGRES') and not app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql://'):
        print("WARNING: USE_POSTGRES is enabled in .env, but DATABASE_URL is not correctly set for PostgreSQL or is missing. Falling back to SQLite.")
    elif app.config.get('USE_POSTGRES') and app.config['SQLALCHEMY_DATABASE_URI'] is None:
        print("WARNING: USE_POSTGRES is enabled in .env, but DATABASE_URL is not set. Falling back to SQLite.")

    login_manager.init_app(app)
    login_manager.unauthorized_handler(lambda: redirect(url_for('home')))
    bcrypt.init_app(app)

    # Create database tables if they don't exist, within an application context
    with app.app_context():
        db.create_all()

    # Now, establish app context for operations that need database access
    with app.app_context():
        app.config['ACTIVE_THEME'] = get_active_theme()
    
    # Initialize Flask-Limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[app.config['RATELIMIT_DEFAULT']],
        storage_uri="memory://", # Use in-memory storage for simplicity, can be Redis for production
        strategy="moving-window"
    )

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({'message': f"Ratelimit exceeded: {e.description}"}), 429

    @app.errorhandler(500)
    def internal_server_error(e):
        # Log the full exception for debugging server-side
        current_app.logger.exception(f"Internal Server Error: {e}")
        return jsonify({'message': 'Internal Server Error', 'details': str(e)}), 500

    # Note: Flask-RESTX Api is initialized within scripts/api_routes.py
    # and its blueprint (api_bp) is registered here.

    from scripts.models import User, Category, Challenge, Submission, ChallengeFlag, FlagSubmission, Award, AwardCategory, FlagAttempt, Hint, UserHint, ApiKey # Import FlagAttempt, Hint, UserHint, ApiKey
    from scripts.code_execution import execute_code_in_sandbox # New: Import for coding challenges

    app.register_blueprint(admin_bp) # Register admin blueprint
    app.register_blueprint(api_key_bp) # Register api_key blueprint
    app.register_blueprint(api_bp) # Register the API blueprint which contains Flask-RESTX

    @app.context_processor
    def inject_global_config():
        """
        Injects global configuration variables into the Jinja2 template context.

        Returns:
            A dictionary containing global configuration variables.
        """
        return dict(disable_signup=app.config['DISABLE_SIGNUP'],
                    active_theme=get_active_theme(),
                    enable_switchboard=app.config['ENABLE_SWITCHBOARD'])

    @app.route('/')
    @app.route('/home')
    def home():
        """
        Renders the home page. Redirects authenticated users to their profile.
        """
        if current_user.is_authenticated:
            return redirect(url_for('challenges'))
        return render_template("index.html")

    @app.route('/register', methods=['GET', 'POST'])
    @limiter.limit(Config.RATELIMIT_REGISTER)
    def register():
        """
        Handles user registration.
        """
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
                                       require_join_code=app.config['REQUIRE_JOIN_CODE'],
                                       preset_usernames_enabled=app.config.get('PRESET_USERNAMES_ENABLED', False))
            
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            email_data = form.email.data if app.config['REQUIRE_EMAIL'] else None
            
            # Determine username
            if app.config.get('PRESET_USERNAMES_ENABLED', False):
                # Generate a unique username
                generated_username_list = generate_usernames(num_to_generate=1)
                if not generated_username_list:
                    flash('Error generating a unique username. Please try again.', 'danger')
                    return render_template('register.html', title='Register', form=form,
                                           require_email=app.config['REQUIRE_EMAIL'],
                                           require_join_code=app.config['REQUIRE_JOIN_CODE'],
                                           preset_usernames_enabled=app.config.get('PRESET_USERNAMES_ENABLED', False))
                new_username = generated_username_list[0]
            else:
                new_username = form.username.data

            user = User(username=new_username, email=email_data, password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
            
            newly_generated_api_key_plain = None
            # Generate an API key for the new user if enabled by GENERATE_API_KEY_ON_REGISTER
            if app.config.get('GENERATE_API_KEY_ON_REGISTER', False):
                db.session.refresh(user) # Ensure user object is fresh for key generation
                newly_generated_api_key_plain = user.generate_new_api_key() # Generate and store the hashed key
                flash(f'Your API Key has been generated: {newly_generated_api_key_plain}. Please save it securely!', 'warning')
            
            flash(f'Your account with username "{new_username}" has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        # Pass configuration flags to the template for conditional rendering of fields
        return render_template('register.html', title='Register', form=form,
                               require_email=app.config['REQUIRE_EMAIL'],
                               require_join_code=app.config['REQUIRE_JOIN_CODE'],
                               preset_usernames_enabled=app.config.get('PRESET_USERNAMES_ENABLED', False))

    @app.route('/login', methods=['GET', 'POST'])
    @limiter.limit(Config.RATELIMIT_LOGIN)
    def login():
        """
        Handles user login.
        """
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        if form.validate_on_submit():
            # Check if the input is an email or username
            user = User.query.filter((User.username == form.username.data) | (User.email == form.username.data)).first()
            if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
                if user.password_reset_required:
                    flash('You must reset your password before continuing.', 'info')
                    login_user(user, remember=form.remember.data) # Log user in to retain context
                    return redirect(url_for('reset_password_force'))
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                response = make_response(redirect(next_page) if next_page else redirect(url_for('home')))
                
                # Set API key cookie if available
                active_key = user.get_active_api_key()
                if active_key and active_key.api_key_plain:
                    response.set_cookie('api_key', active_key.api_key_plain)
                
                return response
            else:
                flash('Login Unsuccessful. Please check username/email and password', 'danger')
        return render_template('login.html', title='Login', form=form)

    @app.route('/logout')
    def logout():
        """
        Logs out the current user and redirects to the home page.
        """
        logout_user()
        return redirect(url_for('home'))

    @app.route('/reset_password_force', methods=['GET', 'POST'])
    @login_required
    def reset_password_force():
        """
        Forces a user to reset their password if password_reset_required is True.
        """
        if not current_user.password_reset_required:
            flash('Your password does not need to be reset.', 'info')
            return redirect(url_for('home'))

        form = PasswordResetForm()
        if form.validate_on_submit():
            current_user.set_password(form.password.data)
            current_user.password_reset_required = False
            db.session.commit()
            flash('Your password has been reset successfully!', 'success')
            return redirect(url_for('home'))
        return render_template('force_password_reset.html', title='Force Password Reset', form=form)

    @app.route('/profile')
    @login_required
    def profile():
        """
        Redirects to the user's own profile page.
        Requires the user to be logged in.
        """
        return user_profile(current_user.username) # Call the user_profile function with current_user's username

    @app.route('/profile/<username>')
    @login_required
    def user_profile(username):
        """
        Displays the profile page for a specific user.

        Args:
            username (str): The username of the user whose profile is to be displayed.
        """
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

        # Fetch all flag attempts for the target user, eager-loading challenge and category details
        flag_attempts = FlagAttempt.query.filter_by(user_id=target_user.id)\
                                       .options(joinedload(FlagAttempt.challenge).joinedload(Challenge.category))\
                                       .order_by(FlagAttempt.timestamp.desc())\
                                       .all()

        # Initialize InlineGiveAwardForm
        give_award_form = None
        if current_user.is_admin:
            give_award_form = InlineGiveAwardForm()
            give_award_form.category.choices = [(ac.id, ac.name) for ac in AwardCategory.query.order_by(AwardCategory.name).all()]

        # API Key information for the profile page
        active_api_key_obj = None
        if current_app.config.get('ENABLE_API_KEY_DISPLAY', False):
            if target_user.id == current_user.id: # Only show current user their own API key info
                active_api_key_obj = current_user.get_active_api_key()

        # --- Chart Data Generation ---
        profile_charts_data = {}
        profile_stats_data = {}

        # 1. Points Over Time Chart and overall statistics
        is_admin_viewer_for_charts = current_user.is_admin
        print(f"DEBUG: current_user.is_admin: {current_user.is_admin}")
        print(f"DEBUG: target_user.id: {target_user.id}, current_user.id: {current_user.id}")
        print(f"DEBUG: is_admin_viewer_for_charts: {is_admin_viewer_for_charts}")
        points_charts, points_stats = get_profile_points_over_time_data(
            target_user, db.session, get_setting,
            Submission, Challenge, Category, User, UTC, timedelta,
            is_admin_viewer=is_admin_viewer_for_charts
        )
        profile_charts_data.update(points_charts)
        profile_stats_data.update(points_stats)

        # 2. Fails vs. Succeeds Chart
        profile_charts_data.update(get_profile_fails_vs_succeeds_data(
            target_user, FlagAttempt, get_setting
        ))

        # 3. Categories per Score Chart
        profile_charts_data.update(get_profile_categories_per_score_data(
            target_user, db.session, Category, Challenge, Submission, func, get_setting
        ))

        # 4. Challenges Complete Chart
        profile_charts_data.update(get_profile_challenges_complete_data(
            target_user, Submission, UTC, timedelta, get_setting
        ))

        return render_template('profile.html', title=f"{target_user.username}'s Profile",
                               user=target_user, submissions=user_submissions, user_rank=user_rank,
                               give_award_form=give_award_form, flag_attempts=flag_attempts,
                               profile_charts_data=profile_charts_data,
                               profile_stats_data=profile_stats_data,
                               active_api_key=active_api_key_obj,
                               enable_api_key_display_template=current_app.config.get('ENABLE_API_KEY_DISPLAY', False),
                               is_admin_viewer_for_charts=is_admin_viewer_for_charts)

    @app.route('/generate_api_key', methods=['POST'])
    @login_required
    def generate_api_key_route():
        """
        Generates a new API key for the current user and redirects to the profile page.
        """
        if not current_app.config.get('ENABLE_API_KEY_DISPLAY', False):
            flash('API Key generation is not enabled.', 'danger')
            return redirect(url_for('profile'))
        
        newly_generated_api_key_plain = current_user.generate_new_api_key()
        flash(f'Your new API Key has been generated: {newly_generated_api_key_plain}. Please save it securely!', 'warning')
        
        response = make_response(redirect(url_for('profile')))
        response.set_cookie('api_key', newly_generated_api_key_plain)
        return response

    @app.route('/challenges')
    @login_required
    def challenges():
        """
        Displays the challenges page, which will be populated dynamically via API.
        Requires the user to be logged in.
        """
        flag_form = FlagSubmissionForm()
        accordion_display_style = get_setting('ACCORDION_DISPLAY_STYLE', 'boxes')
        return render_template('challenges.html', title='Challenges', flag_form=flag_form, current_user_score=current_user.score, accordion_display_style=accordion_display_style)

    # The calculate_points function is now integrated into the Challenge model as a property.
    # This function is no longer needed here.
    # def calculate_points(challenge):
    #     solves = Submission.query.filter_by(challenge_id=challenge.id).count()
    #     if challenge.point_decay_type == 'STATIC':
    #         return challenge.points
    #     elif challenge.point_decay_type == 'LINEAR':
    #         return max(challenge.minimum_points, challenge.points - (solves * challenge.point_decay_rate))
    #     elif challenge.point_decay_type == 'LOGARITHMIC':
    #         if challenge.point_decay_rate == 0:
    #             return challenge.points
    #         return max(challenge.minimum_points, int((((challenge.minimum_points - challenge.points) / (challenge.point_decay_rate ** 2)) * (solves ** 2)) + challenge.points))
    #     return challenge.points

    @app.route('/submit_flag/<int:challenge_id>', methods=['POST'])
    @login_required
    @limiter.limit(Config.RATELIMIT_SUBMIT_FLAG)
    def submit_flag(challenge_id):
        """
        Handles the submission of a flag for a given challenge.

        Args:
            challenge_id (int): The ID of the challenge to submit a flag for.
        """
        form = FlagSubmissionForm()
        if form.validate_on_submit():
            challenge = Challenge.query.options(joinedload(Challenge.flags)).get_or_404(challenge_id)

            # Create a cache of completed challenge IDs for the current user
            # This is required by the updated is_unlocked_for_user method
            user_completed_challenges_cache = {
                current_user.id: {sub.challenge_id for sub in current_user.submissions}
            }

            # Check if the challenge is unlocked for the current user
            if not challenge.is_unlocked_for_user(current_user, user_completed_challenges_cache):
                return jsonify({'success': False, 'message': 'This challenge is currently locked.'})

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

            if challenge.challenge_type == 'CODING':
                # Handle coding challenge submission
                # The submitted "flag" is actually the user's code
                user_code = submitted_flag_content
                
                # --- Static Analysis for malicious patterns ---
                is_safe, static_analysis_message = execute_code_in_sandbox._static_code_analysis(challenge.language, user_code)
                if not is_safe:
                    return jsonify({'success': False, 'message': f'Security check failed: {static_analysis_message}'})
                # --- End Static Analysis ---
                
                execution_result = execute_code_in_sandbox(
                    challenge.language,
                    user_code,
                    challenge.expected_output,
                    challenge.setup_code,
                    challenge.test_case_input
                )

                # Record the attempt
                new_flag_attempt = FlagAttempt(
                    user_id=current_user.id,
                    challenge_id=challenge.id,
                    submitted_flag=user_code, # Store the submitted code
                    is_correct=execution_result.success,
                    timestamp=datetime.now(UTC)
                )
                db.session.add(new_flag_attempt)
                db.session.commit()

                if execution_result.success:
                    # Check if already solved
                    if Submission.query.filter_by(user_id=current_user.id, challenge_id=challenge.id).first():
                        return jsonify({'success': False, 'message': 'You have already solved this coding challenge!'})
                    
                    # Mark challenge as solved
                    points_awarded = challenge.calculated_points
                    new_submission = Submission(user_id=current_user.id, challenge_id=challenge.id, timestamp=datetime.now(UTC))
                    db.session.add(new_submission)
                    current_user.score += points_awarded
                    new_submission.score_at_submission = current_user.score
                    db.session.commit()

                    challenge.update_stripe_status()
                    
                    return jsonify({'success': True, 'message': f'Coding challenge solved! You earned {points_awarded} points!', 'stdout': execution_result.stdout, 'stderr': execution_result.stderr})
                else:
                    message = execution_result.error_message
                    if execution_result.is_timeout:
                        message = "Your code timed out. " + message
                    return jsonify({'success': False, 'message': f'Coding challenge failed: {message}', 'stdout': execution_result.stdout, 'stderr': execution_result.stderr})

            else:
                # Existing logic for traditional flag challenges
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
                        # Use the calculated_points property from the model
                        points_awarded = challenge.calculated_points
                        
                        new_submission = Submission(user_id=current_user.id, challenge_id=challenge.id, timestamp=datetime.now(UTC))
                        db.session.add(new_submission)
                        current_user.score += points_awarded # Update user score
                        new_submission.score_at_submission = current_user.score # Record score at this submission
                        db.session.commit()

                        # Recalculate stripe status for the solved challenge
                        challenge.update_stripe_status()
                        
                        return jsonify({'success': True, 'message': f'Correct Flag! Challenge Solved! You earned {points_awarded} points!'})
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

    @app.route('/reveal_hint/<int:hint_id>', methods=['POST'])
    @login_required
    def reveal_hint(hint_id):
        """
        Handles the revelation of a hint for a given hint ID.

        Args:
            hint_id (int): The ID of the hint to reveal.
        """
        hint = Hint.query.get_or_404(hint_id)
        
        # Check if user has already revealed this hint
        if UserHint.query.filter_by(user_id=current_user.id, hint_id=hint.id).first():
            return jsonify({'success': False, 'message': 'You have already revealed this hint.', 'hint_content': hint.content})

        # Check if user has enough points
        if current_user.score < hint.cost:
            return jsonify({'success': False, 'message': 'Not enough points to reveal this hint.'})

        # Deduct points from user
        current_user.score -= hint.cost
        
        # Record hint revelation
        user_hint = UserHint(user_id=current_user.id, hint_id=hint.id)
        db.session.add(user_hint)
        db.session.commit()

        return jsonify({'success': True, 'message': f'Hint revealed! {hint.cost} points deducted.', 'hint_content': hint.content, 'new_score': current_user.score})

    @app.route('/api/scoreboard_data')
    @login_required
    def scoreboard_data():
        """
        Provides JSON data for the scoreboard, including ranked players and historical scores.
        Requires the user to be logged in.
        """
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
        """
        Returns a JSON list of usernames who have solved a specific challenge.

        Args:
            challenge_id (int): The ID of the challenge.
        """
        challenge = Challenge.query.get_or_404(challenge_id)
        submissions = Submission.query.filter_by(challenge_id=challenge.id).all()
        solvers = [submission.solver.username for submission in submissions]
        return jsonify({'solvers': solvers, 'solver_count': len(solvers)})

    @app.route('/api/challenge_details/<int:challenge_id>')
    @login_required
    def get_challenge_details(challenge_id):
        """
        Returns detailed information about a specific challenge, including hints and completion status.

        Args:
            challenge_id (int): The ID of the challenge.
        """
        try:
            challenge = Challenge.query.options(joinedload(Challenge.hints), joinedload(Challenge.category)).get_or_404(challenge_id)
            
            # Fetch all submissions by all users and build a cache: {user_id: {challenge_id, ...}}
            all_submissions = Submission.query.with_entities(Submission.user_id, Submission.challenge_id).all()
            user_completed_challenges_cache = {}
            for user_id, challenge_id_val in all_submissions:
                user_completed_challenges_cache.setdefault(user_id, set()).add(challenge_id_val)

            # Check if the challenge is unlocked for the current user
            if not challenge.is_unlocked_for_user(current_user, user_completed_challenges_cache):
                return jsonify({'success': False, 'message': 'This challenge is currently locked.'}), 403 # Forbidden

            # Get all hints revealed by the current user for this challenge
            revealed_hint_ids = {uh.hint_id for uh in UserHint.query.filter_by(user_id=current_user.id).all()}

            hints_data = []
            for hint in challenge.hints:
                hints_data.append({
                    'id': hint.id,
                    'title': hint.title, # New: Include hint title
                    'content': hint.content if hint.id in revealed_hint_ids else None, # Only send content if revealed
                    'cost': hint.cost,
                    'is_revealed': hint.id in revealed_hint_ids
                })
            
            # Get completion status and flag counts
            is_completed = Submission.query.filter_by(user_id=current_user.id, challenge_id=challenge.id).first() is not None
            submitted_flags_count = FlagSubmission.query.filter_by(user_id=current_user.id, challenge_id=challenge.id).count()
            total_flags = len(challenge.flags)

            return jsonify({
                'id': challenge.id,
                'name': challenge.name,
                'description': challenge.description,
                'category_name': challenge.category.name, # Added category name
                'points': challenge.calculated_points, # Use the calculated_points property
                'is_completed': is_completed,
                'multi_flag_type': challenge.multi_flag_type,
                'submitted_flags_count': submitted_flags_count,
                'total_flags': total_flags,
                'hints': hints_data,
                'current_user_score': current_user.score, # Pass current user's score for client-side checks
                'language': challenge.language, # New: Pass challenge language for CodeMirror
                'starter_code': challenge.starter_code # New: Pass starter code for CodeMirror
            })
        except Exception as e:
            current_app.logger.error(f"Error in get_challenge_details for challenge_id {challenge_id}: {e}")
            return jsonify({'success': False, 'message': f'Internal server error: {e}'}), 500
    @app.route('/scoreboard')
    @login_required
    def scoreboard():
        """
        Renders the scoreboard page.
        Requires the user to be logged in.
        """
        return render_template('scoreboard.html', title='Scoreboard')

    return app



def create_admin(app, username, password):
    """
    Creates a new super admin user. If a user with the given username already
    exists, it will be deleted and recreated as a super admin.

    Args:
        app: The Flask application instance.
        username (str): The username for the new admin.
        password (str): The password for the new admin.
    """
    with app.app_context():
        from scripts.models import User
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
            print(f"Existing user with username {username} removed before creating new admin.")

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        admin = User(username=username, email=None, password_hash=hashed_password, is_admin=True, is_super_admin=True, hidden=True)
        db.session.add(admin)
        db.session.commit()
        print(f"Super Admin user with username {username} created successfully.")

def recalculate_all_challenge_stripes(app):
    """
    Recalculates and updates the stripe status for all challenges.
    """
    with app.app_context():
        from scripts.models import Challenge
        print("Recalculating stripe statuses for all challenges...")
        challenges = Challenge.query.all()
        for challenge in challenges:
            challenge.update_stripe_status()
            print(f"Updated stripe status for Challenge: {challenge.name}")
        print("All challenge stripe statuses recalculated successfully.")

if __name__ == '__main__':
    from scripts.import_export import import_challenges_from_yaml, import_categories_from_yaml, import_users_from_json, export_data_to_yaml
    parser = argparse.ArgumentParser(description='WindFlag CTF Platform', add_help=False)
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                        help='Show this help message and exit.')
    parser.add_argument('-admin', nargs=2, metavar=('USERNAME', 'PASSWORD'), help='Create an admin user')
    parser.add_argument('-admin-r', type=str, metavar='USERNAME', help='Remove a super admin user. Only super admins can be removed this way.')
    parser.add_argument('-yaml', '-y', type=str, metavar='YAML_FILE', help='Import challenges from a YAML file.')
    parser.add_argument('-users', '-u', type=str, metavar='JSON_FILE', help='Import users from a JSON file.') # New argument
    parser.add_argument('-export-yaml', '-e', nargs='+', metavar=('OUTPUT_FILE', 'DATA_TYPE'), help='Export data to a YAML file. Specify "all", "users", "challenges", "categories", "submissions", "flag_attempts", or "awards".')
    parser.add_argument('-recalculate-stripes', action='store_true', help='Recalculate and update stripe statuses for all challenges.')
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
        app = create_app() # Unpack app and socketio
        test_mode_timeout = None

    if args.admin:
        create_admin(app, args.admin[0], args.admin[1])
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
        # First import categories, then challenges
        import_categories_from_yaml(app, args.yaml)
        import_challenges_from_yaml(app, args.yaml)
    elif args.users: # New conditional for JSON user import
        import_users_from_json(args.users)
    elif args.export_yaml:
        output_file = args.export_yaml[0]
        data_type = 'all'
        if len(args.export_yaml) > 1:
            data_type = args.export_yaml[1]
        export_data_to_yaml(output_file, data_type)
    elif args.recalculate_stripes:
        recalculate_all_challenge_stripes(app)
    else:
        # Otherwise, run the Flask app directly
        if args.test is not None:
            print(f"Running in test mode: server will shut down in {test_mode_timeout} seconds.")
            timer = threading.Timer(test_mode_timeout, os._exit, args=[0])
            timer.start()
        app.run(debug=True, host='0.0.0.0', port=5000)
