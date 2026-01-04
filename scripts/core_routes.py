"""
This module defines the core routes for the WindFlag CTF platform.
It includes routes for user authentication, profile management, challenge interaction,
and scoreboard display.
"""
import os
import json
import mimetypes
from datetime import datetime, UTC, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app, session, make_response, send_from_directory
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from scripts.extensions import db, login_manager, bcrypt, get_setting
from scripts.models import User, Category, Challenge, Submission, ChallengeFlag, FlagSubmission, Award, AwardCategory, FlagAttempt, Hint, UserHint, ApiKey, ChallengeFile
from scripts.forms import RegistrationForm, LoginForm, FlagSubmissionForm, InlineGiveAwardForm, PasswordResetForm
from scripts.theme_utils import get_active_theme
from scripts.chart_data_utils import get_profile_points_over_time_data, get_profile_fails_vs_succeeds_data, get_profile_categories_per_score_data, get_profile_challenges_complete_data
from scripts.utils import generate_usernames, make_datetime_timezone_aware
from scripts.code_execution import execute_code_in_sandbox

core_bp = Blueprint('core', __name__)

@core_bp.app_context_processor
def inject_global_config():
    """
    Injects global configuration variables into the Jinja2 template context.
    """
    return dict(disable_signup=current_app.config['DISABLE_SIGNUP'],
                active_theme=get_active_theme(),
                enable_switchboard=current_app.config['ENABLE_SWITCHBOARD'])

@core_bp.route('/')
@core_bp.route('/home')
def home():
    """
    Renders the home page. Redirects authenticated users to their profile.
    """
    if current_user.is_authenticated:
        return redirect(url_for('core.challenges'))
    return render_template("index.html")

@core_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration.
    """
    if current_app.config['DISABLE_SIGNUP']:
        flash('User registration is currently disabled.', 'info')
        return redirect(url_for('core.home'))
    if current_user.is_authenticated:
        return redirect(url_for('core.home'))
    
    form = RegistrationForm(current_app.config)
    if form.validate_on_submit():
        if current_app.config['REQUIRE_JOIN_CODE'] and form.join_code.data != current_app.config['JOIN_CODE']:
            flash('Invalid join code.', 'danger')
            return render_template('register.html', title='Register', form=form,
                                   require_email=current_app.config['REQUIRE_EMAIL'],
                                   require_join_code=current_app.config['REQUIRE_JOIN_CODE'],
                                   preset_usernames_enabled=current_app.config.get('PRESET_USERNAMES_ENABLED', False))
        
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        email_data = form.email.data if current_app.config['REQUIRE_EMAIL'] else None
        
        if current_app.config.get('PRESET_USERNAMES_ENABLED', False):
            generated_username_list = generate_usernames(num_to_generate=1)
            if not generated_username_list:
                flash('Error generating a unique username. Please try again.', 'danger')
                return render_template('register.html', title='Register', form=form,
                                       require_email=current_app.config['REQUIRE_EMAIL'],
                                       require_join_code=current_app.config['REQUIRE_JOIN_CODE'],
                                       preset_usernames_enabled=current_app.config.get('PRESET_USERNAMES_ENABLED', False))
            new_username = generated_username_list[0]
        else:
            new_username = form.username.data

        user = User(username=new_username, email=email_data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        if current_app.config.get('GENERATE_API_KEY_ON_REGISTER', False):
            db.session.refresh(user)
            user.generate_new_api_key()
        
        flash(f'Your account with username "{new_username}" has been created! You are now able to log in', 'success')
        return redirect(url_for('core.login'))
        
    return render_template('register.html', title='Register', form=form,
                           require_email=current_app.config['REQUIRE_EMAIL'],
                           require_join_code=current_app.config['REQUIRE_JOIN_CODE'],
                           preset_usernames_enabled=current_app.config.get('PRESET_USERNAMES_ENABLED', False))

@core_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.
    """
    if current_user.is_authenticated:
        return redirect(url_for('core.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.username == form.username.data) | (User.email == form.username.data)).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            if user.password_reset_required:
                flash('You must reset your password before continuing.', 'info')
                login_user(user, remember=form.remember.data)
                return redirect(url_for('core.reset_password_force'))
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            response = make_response(redirect(next_page) if next_page else redirect(url_for('core.home')))
            
            active_key = user.get_active_api_key()
            if active_key and active_key.api_key_plain:
                response.set_cookie('windflag_api_key', active_key.api_key_plain, samesite='Lax')
            
            return response
        else:
            flash('Login Unsuccessful. Please check username/email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@core_bp.route('/logout')
def logout():
    """
    Logs out the current user and redirects to the home page.
    """
    logout_user()
    return redirect(url_for('core.home'))

@core_bp.route('/reset_password_force', methods=['GET', 'POST'])
@login_required
def reset_password_force():
    """
    Forces a user to reset their password if password_reset_required is True.
    """
    if not current_user.password_reset_required:
        flash('Your password does not need to be reset.', 'info')
        return redirect(url_for('core.home'))

    form = PasswordResetForm()
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        current_user.password_reset_required = False
        db.session.commit()
        flash('Your password has been reset successfully!', 'success')
        return redirect(url_for('core.home'))
    return render_template('force_password_reset.html', title='Force Password Reset', form=form)

@core_bp.route('/profile')
@login_required
def profile():
    """
    Redirects to the user's own profile page.
    """
    return user_profile(current_user.username)

@core_bp.route('/profile/<username>')
@login_required
def user_profile(username):
    """
    Displays the profile page for a specific user.
    """
    user_query = User.query.filter_by(username=username)

    if current_user.is_admin:
        user_query = user_query.options(
            joinedload(User.awards_received).joinedload(Award.category),
            joinedload(User.awards_received).joinedload(Award.giver)
        )
    
    target_user = user_query.first_or_404()

    if target_user.hidden and not current_user.is_admin:
        flash('You do not have permission to view this profile.', 'danger')
        return redirect(url_for('core.home'))

    ranked_users = db.session.query(
        User.id,
        User.username,
        User.score,
        func.rank().over(order_by=User.score.desc()).label('rank')
    ).filter(User.hidden == False).subquery()

    user_rank_data = db.session.query(ranked_users.c.rank)
                               .filter(ranked_users.c.id == target_user.id)
                               .first()
    user_rank = user_rank_data.rank if user_rank_data else None

    user_submissions = Submission.query.filter_by(user_id=target_user.id)
                                       .options(joinedload(Submission.challenge_rel).joinedload(Challenge.category))
                                       .order_by(Submission.timestamp.desc())
                                       .all()

    flag_attempts = FlagAttempt.query.filter_by(user_id=target_user.id)
                                   .options(joinedload(FlagAttempt.challenge).joinedload(Challenge.category))
                                   .order_by(FlagAttempt.timestamp.desc())
                                   .all()

    give_award_form = None
    if current_user.is_admin:
        give_award_form = InlineGiveAwardForm()
        give_award_form.category.choices = [(ac.id, ac.name) for ac in AwardCategory.query.order_by(AwardCategory.name).all()]

    active_api_key_obj = None
    if current_app.config.get('ENABLE_API_KEY_DISPLAY', False):
        if target_user.id == current_user.id:
            active_api_key_obj = current_user.get_active_api_key()

    profile_charts_data = {}
    profile_stats_data = {}

    is_admin_viewer_for_charts = current_user.is_admin
    points_charts, points_stats = get_profile_points_over_time_data(
        target_user, db.session, get_setting,
        Submission, Challenge, Category, User, UTC, timedelta,
        is_admin_viewer=is_admin_viewer_for_charts
    )
    profile_charts_data.update(points_charts)
    profile_stats_data.update(points_stats)

    profile_charts_data.update(get_profile_fails_vs_succeeds_data(
        target_user, FlagAttempt, get_setting
    ))

    profile_charts_data.update(get_profile_categories_per_score_data(
        target_user, db.session, Category, Challenge, Submission, func, get_setting
    ))

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

@core_bp.route('/generate_api_key', methods=['POST'])
@login_required
def generate_api_key_route():
    """
    Generates a new API key for the current user and redirects to the profile page.
    """
    if not current_app.config.get('ENABLE_API_KEY_DISPLAY', False):
        flash('API Key generation is not enabled.', 'danger')
        return redirect(url_for('core.profile'))
    
    newly_generated_api_key_plain = current_user.generate_new_api_key()
    flash('API Key generated successfully.', 'success')
    
    response = make_response(redirect(url_for('core.profile')))
    response.set_cookie('windflag_api_key', newly_generated_api_key_plain, samesite='Lax')
    return response

@core_bp.route('/challenges')
@login_required
def challenges():
    """
    Displays the challenges page.
    """
    flag_form = FlagSubmissionForm()
    accordion_display_style = get_setting('ACCORDION_DISPLAY_STYLE', 'boxes')
    return render_template('challenges.html', title='Challenges', flag_form=flag_form, current_user_score=current_user.score, accordion_display_style=accordion_display_style)

@core_bp.route('/<category_name>/<challenge_name>')
@login_required
def view_challenge_by_name(category_name, challenge_name):
    """
    Redirects to the challenges page with a specific challenge modal opened.
    """
    formatted_category_name = category_name.replace('_', ' ')
    formatted_challenge_name = challenge_name.replace('_', ' ')

    category = Category.query.filter_by(name=formatted_category_name).first()
    if not category:
        flash(f"Category '{formatted_category_name}' not found.", 'danger')
        return redirect(url_for('core.challenges'))

    challenge = Challenge.query.filter_by(name=formatted_challenge_name, category_id=category.id).first()
    if not challenge:
        flash(f"Challenge '{formatted_challenge_name}' not found in category '{formatted_category_name}'.", 'danger')
        return redirect(url_for('core.challenges'))
    
    return redirect(url_for('core.challenges', challenge_id=challenge.id))

@core_bp.route('/download_file/<int:file_id>')
@login_required
def download_challenge_file(file_id):
    """
    Allows users to download a file attached to a challenge.
    """
    file = ChallengeFile.query.get_or_404(file_id)
    challenge = Challenge.query.get_or_404(file.challenge_id)
    
    user_completed_challenges_cache = {
        current_user.id: {sub.challenge_id for sub in current_user.submissions}
    }
    
    if not challenge.is_unlocked_for_user(current_user, user_completed_challenges_cache):
         flash('You do not have permission to access this file.', 'danger')
         return redirect(url_for('core.challenges'))

    directory = os.path.join(current_app.config['UPLOAD_FOLDER'], 'challenge_files')
    return send_from_directory(directory, file.storage_filename, as_attachment=True, download_name=file.filename)

@core_bp.route('/submit_flag/<int:challenge_id>', methods=['POST'])
@login_required
def submit_flag(challenge_id):
    """
    Handles the submission of a flag for a given challenge.
    """
    form = FlagSubmissionForm()
    if form.validate_on_submit():
        challenge = Challenge.query.options(joinedload(Challenge.flags)).get_or_404(challenge_id)

        user_completed_challenges_cache = {
            current_user.id: {sub.challenge_id for sub in current_user.submissions}
        }

        if not challenge.is_unlocked_for_user(current_user, user_completed_challenges_cache):
            return jsonify({'success': False, 'message': 'This challenge is currently locked.'})

        if Submission.query.filter_by(user_id=current_user.id, challenge_id=challenge.id).first():
            new_flag_attempt = FlagAttempt(
                user_id=current_user.id,
                challenge_id=challenge.id,
                submitted_flag=form.flag.data,
                is_correct=False,
                timestamp=datetime.now(UTC)
            )
            db.session.add(new_flag_attempt)
            db.session.commit()
            return jsonify({'success': False, 'message': 'You have already solved this challenge!'})

        submitted_flag_content = form.flag.data

        if challenge.challenge_type == 'CODING':
            user_code = submitted_flag_content
            from scripts.code_execution import _static_code_analysis
            is_safe, static_analysis_message = _static_code_analysis(challenge.language, user_code)
            if not is_safe:
                return jsonify({'success': False, 'message': f'Security check failed: {static_analysis_message}'})
            
            execution_result = execute_code_in_sandbox(
                challenge.language,
                user_code,
                challenge.expected_output,
                challenge.setup_code,
                challenge.test_case_input
            )

            new_flag_attempt = FlagAttempt(
                user_id=current_user.id,
                challenge_id=challenge.id,
                submitted_flag=user_code,
                is_correct=execution_result.success,
                timestamp=datetime.now(UTC)
            )
            db.session.add(new_flag_attempt)
            db.session.commit()

            if execution_result.success:
                points_awarded = challenge.calculated_points
                new_submission = Submission(user_id=current_user.id, challenge_id=challenge.id, timestamp=datetime.now(UTC), score_at_submission=current_user.score + points_awarded)
                db.session.add(new_submission)
                current_user.score += points_awarded
                db.session.commit()
                challenge.update_stripe_status()
                return jsonify({'success': True, 'message': f'Coding challenge solved! You earned {points_awarded} points!', 'stdout': execution_result.stdout, 'stderr': execution_result.stderr})
            else:
                message = execution_result.error_message
                if execution_result.is_timeout:
                    message = "Your code timed out. " + message
                return jsonify({'success': False, 'message': f'Coding challenge failed: {message}', 'stdout': execution_result.stdout, 'stderr': execution_result.stderr})

        else:
            correct_flag_found = None
            for cf in challenge.flags:
                if challenge.case_sensitive:
                    if cf.flag_content == submitted_flag_content:
                        correct_flag_found = cf
                        break
                else:
                    if cf.flag_content.lower() == submitted_flag_content.lower():
                        correct_flag_found = cf
                        break
            
            new_flag_attempt = FlagAttempt(
                user_id=current_user.id,
                challenge_id=challenge.id,
                submitted_flag=submitted_flag_content,
                is_correct=(correct_flag_found is not None),
                timestamp=datetime.now(UTC)
            )
            db.session.add(new_flag_attempt)
            db.session.commit()

            if correct_flag_found:
                if FlagSubmission.query.filter_by(user_id=current_user.id, challenge_flag_id=correct_flag_found.id).first():
                    return jsonify({'success': False, 'message': 'You have already submitted this specific flag.'})
                
                new_flag_submission = FlagSubmission(
                    user_id=current_user.id,
                    challenge_id=challenge.id,
                    challenge_flag_id=correct_flag_found.id,
                    timestamp=datetime.now(UTC)
                )
                db.session.add(new_flag_submission)
                db.session.commit()

                is_challenge_solved = False
                user_submitted_flags_for_challenge = FlagSubmission.query.filter_by(
                    user_id=current_user.id,
                    challenge_id=challenge.id
                ).count()
                
                total_flags_for_challenge = len(challenge.flags)

                if challenge.multi_flag_type == 'SINGLE' or challenge.multi_flag_type == 'ANY':
                    is_challenge_solved = True
                elif challenge.multi_flag_type == 'ALL':
                    if user_submitted_flags_for_challenge == total_flags_for_challenge:
                        is_challenge_solved = True
                elif challenge.multi_flag_type == 'N_OF_M':
                    if challenge.multi_flag_threshold and user_submitted_flags_for_challenge >= challenge.multi_flag_threshold:
                        is_challenge_solved = True
                
                if is_challenge_solved:
                    points_awarded = challenge.calculated_points
                    new_submission = Submission(user_id=current_user.id, challenge_id=challenge.id, timestamp=datetime.now(UTC), score_at_submission=current_user.score + points_awarded)
                    db.session.add(new_submission)
                    current_user.score += points_awarded
                    db.session.commit()
                    challenge.update_stripe_status()
                    return jsonify({'success': True, 'message': f'Correct Flag! Challenge Solved! You earned {points_awarded} points!'})
                else:
                    return jsonify({
                        'success': True,
                        'message': f'Correct Flag! You have submitted {user_submitted_flags_for_challenge} of {total_flags_for_challenge} flags for this challenge.'
                    })
            else:
                return jsonify({'success': False, 'message': 'Incorrect Flag. Please try again.'})
    return jsonify({'success': False, 'message': 'Invalid form submission.'})

@core_bp.route('/reveal_hint/<int:hint_id>', methods=['POST'])
@login_required
def reveal_hint(hint_id):
    """
    Handles the revelation of a hint.
    """
    hint = Hint.query.get_or_404(hint_id)
    
    if UserHint.query.filter_by(user_id=current_user.id, hint_id=hint.id).first():
        return jsonify({'success': False, 'message': 'You have already revealed this hint.', 'hint_content': hint.content})

    if current_user.score < hint.cost:
        return jsonify({'success': False, 'message': 'Not enough points to reveal this hint.'})

    current_user.score -= hint.cost
    user_hint = UserHint(user_id=current_user.id, hint_id=hint.id)
    db.session.add(user_hint)
    db.session.commit()

    return jsonify({'success': True, 'message': f'Hint revealed! {hint.cost} points deducted.', 'hint_content': hint.content, 'new_score': current_user.score})

@core_bp.route('/api/scoreboard_data')
@login_required
def scoreboard_data():
    """
    Provides JSON data for the scoreboard.
    """
    try:
        top_x = int(get_setting('TOP_X_SCOREBOARD', '10'))

        all_players_ranked_query = db.session.query(
            User.username,
            func.coalesce(func.sum(Challenge.points), 0).label('score'),
            func.max(Submission.timestamp).label('last_submission')
        ).outerjoin(Submission, User.id == Submission.user_id)
         .outerjoin(Challenge, Submission.challenge_id == Challenge.id)
         .filter(User.hidden == False)
         .group_by(User.id, User.username)
         .order_by(func.coalesce(func.sum(Challenge.points), 0).desc(), func.max(Submission.timestamp).asc())
         .all()
        
        all_players_ranked = [{'username': user_data.username, 'score': user_data.score} for user_data in all_players_ranked_query]

        top_users_query = User.query.filter_by(hidden=False).order_by(User.score.desc()).limit(top_x).all()
        top_players_history = {}
        
        for user in top_users_query:
            user_history_list = []
            user_submissions = Submission.query.filter_by(user_id=user.id).order_by(Submission.timestamp.asc()).all()

            if user_submissions:
                initial_timestamp = user_submissions[0].timestamp - timedelta(microseconds=1)
                user_history_list.append({'x': initial_timestamp.isoformat(), 'y': 0})
            else:
                user_history_list.append({'x': datetime.now(UTC).isoformat(), 'y': 0})

            for submission in user_submissions:
                user_history_list.append({'x': submission.timestamp.isoformat(), 'y': submission.score_at_submission})
            
            top_players_history[user.username] = user_history_list

        graph_type = get_setting('SCOREBOARD_GRAPH_TYPE', 'line')

        return jsonify({
            'top_players_history': top_players_history,
            'all_players_ranked': all_players_ranked,
            'graph_type': graph_type
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching scoreboard data: {e}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@core_bp.route('/api/challenge/<int:challenge_id>/solvers')
@login_required
def get_challenge_solvers(challenge_id):
    """
    Returns a JSON list of usernames who have solved a specific challenge.
    """
    challenge = Challenge.query.get_or_404(challenge_id)
    submissions = Submission.query.filter_by(challenge_id=challenge.id).all()
    solvers = [submission.solver.username for submission in submissions]
    return jsonify({'solvers': solvers, 'solver_count': len(solvers)})

@core_bp.route('/api/challenge_details/<int:challenge_id>')
@login_required
def get_challenge_details(challenge_id):
    """
    Returns detailed information about a specific challenge.
    """
    try:
        challenge = Challenge.query.options(joinedload(Challenge.hints), joinedload(Challenge.category)).get_or_404(challenge_id)
        
        category_name = challenge.category.name if challenge.category else "Uncategorized"

        all_submissions = Submission.query.with_entities(Submission.user_id, Submission.challenge_id).all()
        user_completed_challenges_cache = {}
        for user_id, c_id in all_submissions:
            user_completed_challenges_cache.setdefault(user_id, set()).add(c_id)

        if not challenge.is_unlocked_for_user(current_user, user_completed_challenges_cache):
            return jsonify({'success': False, 'message': 'This challenge is currently locked.'}), 403

        revealed_hint_ids = {uh.hint_id for uh in UserHint.query.filter_by(user_id=current_user.id).all()}

        hints_data = [{
            'id': hint.id,
            'title': hint.title,
            'content': hint.content if hint.id in revealed_hint_ids else None,
            'cost': hint.cost,
            'is_revealed': hint.id in revealed_hint_ids
        } for hint in challenge.hints]

        files_data = [{
            'id': file.id,
            'filename': file.filename,
            'download_url': url_for('core.download_challenge_file', file_id=file.id)
        } for file in challenge.files]
        
        is_completed = Submission.query.filter_by(user_id=current_user.id, challenge_id=challenge.id).first() is not None
        submitted_flags_count = FlagSubmission.query.filter_by(user_id=current_user.id, challenge_id=challenge.id).count()
        total_flags = len(challenge.flags)

        response_data = {
            'id': challenge.id,
            'name': challenge.name,
            'description': challenge.description,
            'category_name': category_name,
            'points': challenge.calculated_points,
            'is_completed': is_completed,
            'multi_flag_type': challenge.multi_flag_type,
            'submitted_flags_count': submitted_flags_count,
            'total_flags': total_flags,
            'hints': hints_data,
            'files': files_data,
            'current_user_score': current_user.score,
            'language': challenge.language,
            'starter_code': challenge.starter_code
        }
        return jsonify(response_data)
    except Exception as e:
        current_app.logger.error(f"Error in get_challenge_details for challenge_id {challenge_id}: {e}", exc_info=True)
        return jsonify({'success': False, 'message': f'Internal server error: {e}'}), 500

@core_bp.route('/scoreboard')
@login_required
def scoreboard():
    """
    Renders the scoreboard page.
    """
    return render_template('scoreboard.html', title='Scoreboard')
