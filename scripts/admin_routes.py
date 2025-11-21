"""
This module defines the administrative routes and functions for the WindFlag CTF platform.
It includes routes for managing categories, challenges, users, award categories, and viewing analytics.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from scripts.extensions import db, get_setting
from scripts.models import Category, Challenge, Submission, User, Setting, ChallengeFlag, FlagSubmission, AwardCategory, Award, FlagAttempt
from scripts.forms import CategoryForm, ChallengeForm, AdminSettingsForm, AwardCategoryForm, InlineGiveAwardForm, _get_timezone_choices
from functools import wraps
from sqlalchemy import func
from sqlalchemy.orm import joinedload # Import joinedload for eager loading
import pytz # New: For timezone handling
from datetime import datetime, UTC # New: For datetime and UTC timezone

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """
    Decorator to ensure that only authenticated administrators can access a route.
    Redirects non-admin users to the home page with a flash message.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def index():
    """
    Renders the admin dashboard index page.
    Requires admin privileges.
    """
    return render_template('admin/index.html', title='Admin Dashboard')

def _update_setting(key, value):
    """
    Helper function to update an existing setting or create it if it doesn't exist.
    """
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        setting.value = str(value)
    else:
        setting = Setting(key=key, value=str(value))
        db.session.add(setting)

@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    """
    Handles the display and updating of administrative settings.
    Requires admin privileges.
    """
    form = AdminSettingsForm()
    if form.validate_on_submit():
        _update_setting('TOP_X_SCOREBOARD', form.top_x_scoreboard.data)
        _update_setting('SCOREBOARD_GRAPH_TYPE', form.scoreboard_graph_type.data)
        _update_setting('PROFILE_POINTS_OVER_TIME_CHART_ENABLED', form.profile_points_over_time_chart_enabled.data)
        _update_setting('PROFILE_FAILS_VS_SUCCEEDS_CHART_ENABLED', form.profile_fails_vs_succeeds_chart_enabled.data)
        _update_setting('PROFILE_CATEGORIES_PER_SCORE_CHART_ENABLED', form.profile_categories_per_score_chart_enabled.data)
        _update_setting('PROFILE_CHALLENGES_COMPLETE_CHART_ENABLED', form.profile_challenges_complete_chart_enabled.data)
        _update_setting('TIMEZONE', form.timezone.data) # New: Save timezone setting

        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.admin_settings'))
    elif request.method == 'GET':
        form.top_x_scoreboard.data = int(get_setting('TOP_X_SCOREBOARD', '10'))
        form.scoreboard_graph_type.data = get_setting('SCOREBOARD_GRAPH_TYPE', 'line')
        form.profile_points_over_time_chart_enabled.data = get_setting('PROFILE_POINTS_OVER_TIME_CHART_ENABLED', 'True').lower() == 'true'
        form.profile_fails_vs_succeeds_chart_enabled.data = get_setting('PROFILE_FAILS_VS_SUCCEEDS_CHART_ENABLED', 'True').lower() == 'true'
        form.profile_categories_per_score_chart_enabled.data = get_setting('PROFILE_CATEGORIES_PER_SCORE_CHART_ENABLED', 'True').lower() == 'true'
        form.profile_challenges_complete_chart_enabled.data = get_setting('PROFILE_CHALLENGES_COMPLETE_CHART_ENABLED', 'True').lower() == 'true'
        form.timezone.data = get_setting('TIMEZONE', 'Australia/Sydney') # New: Load timezone setting
    return render_template('admin/settings.html', title='Admin Settings', form=form)

# Category CRUD
@admin_bp.route('/categories')
@admin_required
def manage_categories():
    """
    Displays a list of all challenge categories for management.
    Requires admin privileges.
    """
    categories = Category.query.all()
    return render_template('admin/manage_categories.html', title='Manage Categories', categories=categories)

@admin_bp.route('/category/new', methods=['GET', 'POST'])
@admin_required
def new_category():
    """
    Handles the creation of a new challenge category.
    Requires admin privileges.
    """
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Category has been created!', 'success')
        return redirect(url_for('admin.manage_categories'))
    return render_template('admin/create_category.html', title='New Category', form=form)

@admin_bp.route('/category/<int:category_id>/update', methods=['GET', 'POST'])
@admin_required
def update_category(category_id):
    """
    Handles the updating of an existing challenge category.

    Args:
        category_id (int): The ID of the category to update.
    Requires admin privileges.
    """
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category has been updated!', 'success')
        return redirect(url_for('admin.manage_categories'))
    elif request.method == 'GET':
        form.name.data = category.name
    return render_template('admin/create_category.html', title='Update Category', form=form)

@admin_bp.route('/category/<int:category_id>/delete', methods=['POST'])
@admin_required
def delete_category(category_id):
    """
    Handles the deletion of a challenge category.

    Args:
        category_id (int): The ID of the category to delete.
    Requires admin privileges.
    """
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category has been deleted!', 'success')
    return redirect(url_for('admin.manage_categories'))

# Challenge CRUD
@admin_bp.route('/challenges')
@admin_required
def manage_challenges():
    """
    Displays a list of all challenges for management.
    Requires admin privileges.
    """
    challenges = Challenge.query.all()
    return render_template('admin/manage_challenges.html', title='Manage Challenges', challenges=challenges)

def _get_prerequisite_challenge_choices():
    """
    Prepares choices for the prerequisite_challenge_ids_input SelectMultipleField,
    grouped by category.
    """
    categories = Category.query.options(joinedload(Category.challenges)).order_by(Category.name).all()
    choices = []
    for category in categories:
        category_challenges = []
        for challenge in category.challenges:
            category_challenges.append((challenge.id, challenge.name)) # Removed (ID: {challenge.id})
        if category_challenges:
            choices.append((category.name, category_challenges))
    return choices

def _get_category_choices():
    """
    Prepares choices for a SelectMultipleField with categories.
    """
    categories = Category.query.order_by(Category.name).all()
    choices = [(c.id, c.name) for c in categories]
    return choices

def _get_timezone_choices():
    """
    Returns a list of common timezone choices for a SelectField.
    """
    return [(tz, tz) for tz in pytz.common_timezones]

@admin_bp.route('/challenge/new', methods=['GET', 'POST'])
@admin_required
def new_challenge():
    """
    Handles the creation of a new challenge.
    Allows creating a new category or assigning to an existing one.
    Requires admin privileges.
    """
    form = ChallengeForm()
    form.category.choices.extend([(c.id, c.name) for c in Category.query.all()])
    form.prerequisite_challenge_ids_input.choices = _get_prerequisite_challenge_choices()
    form.prerequisite_count_category_ids_input.choices = _get_category_choices()
    form.timezone.choices = _get_timezone_choices() # Set timezone choices

    if form.validate_on_submit():
        category_id = None
        if form.new_category_name.data:
            new_category = Category(name=form.new_category_name.data)
            db.session.add(new_category)
            db.session.commit()
            category_id = new_category.id
        else:
            category_id = form.category.data

        # Handle timezone conversion for unlock_date_time and unlock_point_reduction_target_date
        local_timezone_name = form.timezone.data # Use selected timezone from form
        local_tz = pytz.timezone(local_timezone_name)

        unlock_date_time_utc = None
        if form.unlock_date_time.data:
            # Assume form data is in local timezone, localize it, then convert to UTC
            # For DateField, we need to add a default time (e.g., midnight) before localizing
            localized_dt = local_tz.localize(datetime.combine(form.unlock_date_time.data, datetime.min.time()))
            unlock_date_time_utc = localized_dt.astimezone(UTC)

        unlock_point_reduction_target_date_utc = None
        if form.unlock_point_reduction_target_date.data:
            localized_dt = local_tz.localize(datetime.combine(form.unlock_point_reduction_target_date.data, datetime.min.time()))
            unlock_point_reduction_target_date_utc = localized_dt.astimezone(UTC)

        challenge = Challenge(name=form.name.data, description=form.description.data,
                              points=form.points.data,
                              minimum_points=form.minimum_points.data,
                              point_decay_type=form.point_decay_type.data,
                              point_decay_rate=form.point_decay_rate.data,
                              proactive_decay=form.proactive_decay.data,
                              case_sensitive=form.case_sensitive.data,
                              category_id=category_id,
                              multi_flag_type=form.multi_flag_type.data,
                              multi_flag_threshold=form.multi_flag_threshold.data if form.multi_flag_type.data == 'N_OF_M' else None,
                              unlock_type=form.unlock_type.data,
                              prerequisite_percentage_value=form.prerequisite_percentage_value.data,
                              prerequisite_count_value=form.prerequisite_count_value.data,
                              prerequisite_count_category_ids=form.prerequisite_count_category_ids_input.data,
                              prerequisite_challenge_ids=form.prerequisite_challenge_ids_input.data,
                              unlock_date_time=unlock_date_time_utc,
                              unlock_point_reduction_type=form.unlock_point_reduction_type.data,
                              unlock_point_reduction_value=form.unlock_point_reduction_value.data,
                              unlock_point_reduction_target_date=unlock_point_reduction_target_date_utc)
        db.session.add(challenge)
        db.session.commit() # Commit to get challenge.id

        # Add flags
        flags_content = [f.strip() for f in form.flags_input.data.split('\n') if f.strip()]
        for flag_content in flags_content:
            challenge_flag = ChallengeFlag(challenge_id=challenge.id, flag_content=flag_content)
            db.session.add(challenge_flag)
        db.session.commit()

        flash('Challenge has been created!', 'success')
        return redirect(url_for('admin.manage_challenges'))
    return render_template('admin/create_challenge.html', title='New Challenge', form=form,
                           is_current_user_super_admin=bool(current_user.is_super_admin),
                           users_super_admin_status={}, # Not directly used here, but admin.js expects it
                           current_user_id=current_user.id)

@admin_bp.route('/challenge/<int:challenge_id>/update', methods=['GET', 'POST'])
@admin_required
def update_challenge(challenge_id):
    """
    Handles the updating of an existing challenge.

    Args:
        challenge_id (int): The ID of the challenge to update.
    Requires admin privileges.
    """
    challenge = Challenge.query.get_or_404(challenge_id)
    form = ChallengeForm()
    form.category.choices.extend([(c.id, c.name) for c in Category.query.all()])
    form.prerequisite_challenge_ids_input.choices = _get_prerequisite_challenge_choices()
    form.prerequisite_count_category_ids_input.choices = _get_category_choices()
    form.timezone.choices = _get_timezone_choices() # Set timezone choices

    if form.validate_on_submit():
        category_id = None
        if form.new_category_name.data:
            new_category = Category(name=form.new_category_name.data)
            db.session.add(new_category)
            db.session.commit()
            category_id = new_category.id
        else:
            category_id = form.category.data

        # Handle timezone conversion for unlock_date_time and unlock_point_reduction_target_date
        local_timezone_name = form.timezone.data # Use selected timezone from form
        local_tz = pytz.timezone(local_timezone_name)

        unlock_date_time_utc = None
        if form.unlock_date_time.data:
            # Assume form data is in local timezone, localize it, then convert to UTC
            # For DateField, we need to add a default time (e.g., midnight) before localizing
            localized_dt = local_tz.localize(datetime.combine(form.unlock_date_time.data, datetime.min.time()))
            unlock_date_time_utc = localized_dt.astimezone(UTC)

        unlock_point_reduction_target_date_utc = None
        if form.unlock_point_reduction_target_date.data:
            localized_dt = local_tz.localize(datetime.combine(form.unlock_point_reduction_target_date.data, datetime.min.time()))
            unlock_point_reduction_target_date_utc = localized_dt.astimezone(UTC)

        challenge.name = form.name.data
        challenge.description = form.description.data
        challenge.points = form.points.data
        challenge.minimum_points = form.minimum_points.data
        challenge.point_decay_type = form.point_decay_type.data
        challenge.point_decay_rate = form.point_decay_rate.data
        challenge.proactive_decay = form.proactive_decay.data
        challenge.case_sensitive = form.case_sensitive.data
        challenge.category_id = category_id
        challenge.multi_flag_type = form.multi_flag_type.data
        challenge.multi_flag_threshold = form.multi_flag_threshold.data if form.multi_flag_type.data == 'N_OF_M' else None
        
        challenge.unlock_type = form.unlock_type.data
        challenge.prerequisite_percentage_value = form.prerequisite_percentage_value.data
        challenge.prerequisite_count_value = form.prerequisite_count_value.data
        challenge.prerequisite_count_category_ids = form.prerequisite_count_category_ids_input.data
        challenge.prerequisite_challenge_ids = form.prerequisite_challenge_ids_input.data
        challenge.unlock_date_time = unlock_date_time_utc
        challenge.unlock_point_reduction_type = form.unlock_point_reduction_type.data
        challenge.unlock_point_reduction_value = form.unlock_point_reduction_value.data
        challenge.unlock_point_reduction_target_date = unlock_point_reduction_target_date_utc
        
        # Delete existing flags and add new ones
        ChallengeFlag.query.filter_by(challenge_id=challenge.id).delete()
        flags_content = [f.strip() for f in form.flags_input.data.split('\n') if f.strip()]
        for flag_content in flags_content:
            challenge_flag = ChallengeFlag(challenge_id=challenge.id, flag_content=flag_content)
            db.session.add(challenge_flag)
        
        db.session.commit()
        flash('Challenge has been updated!', 'success')
        return redirect(url_for('admin.manage_challenges'))
    elif request.method == 'GET':
        form.name.data = challenge.name
        form.description.data = challenge.description
        form.points.data = challenge.points
        form.minimum_points.data = challenge.minimum_points
        form.point_decay_type.data = challenge.point_decay_type
        form.point_decay_rate.data = challenge.point_decay_rate
        form.proactive_decay.data = challenge.proactive_decay
        form.case_sensitive.data = challenge.case_sensitive
        form.category.data = challenge.category_id
        form.multi_flag_type.data = challenge.multi_flag_type
        form.multi_flag_threshold.data = challenge.multi_flag_threshold
        form.flags_input.data = "\n".join([f.flag_content for f in challenge.flags])

        form.unlock_type.data = challenge.unlock_type
        form.prerequisite_percentage_value.data = challenge.prerequisite_percentage_value
        form.prerequisite_count_value.data = challenge.prerequisite_count_value
        form.prerequisite_count_category_ids_input.data = challenge.prerequisite_count_category_ids
        form.prerequisite_challenge_ids_input.data = challenge.prerequisite_challenge_ids

        # Convert UTC datetimes from DB to local timezone for display
        # Use the default timezone for display if not explicitly set in the form
        form.timezone.data = current_app.config['TIMEZONE'] # Set default timezone for display
        local_tz = pytz.timezone(form.timezone.data)
        
        if challenge.unlock_date_time:
            # For DateField, we only care about the date part
            form.unlock_date_time.data = challenge.unlock_date_time.astimezone(local_tz).date()
        else:
            form.unlock_date_time.data = None

        if challenge.unlock_point_reduction_target_date:
            form.unlock_point_reduction_target_date.data = challenge.unlock_point_reduction_target_date.astimezone(local_tz).date()
        else:
            form.unlock_point_reduction_target_date.data = None

    return render_template('admin/create_challenge.html', title='Update Challenge', form=form,
                           is_current_user_super_admin=bool(current_user.is_super_admin),
                           users_super_admin_status={}, # Not directly used here, but admin.js expects it
                           current_user_id=current_user.id)

@admin_bp.route('/challenge/<int:challenge_id>/delete', methods=['POST'])
@admin_required
def delete_challenge(challenge_id):
    """
    Handles the deletion of a challenge.

    Args:
        challenge_id (int): The ID of the challenge to delete.
    Requires admin privileges.
    """
    challenge = Challenge.query.get_or_404(challenge_id)
    db.session.delete(challenge)
    db.session.commit()
    flash('Challenge has been deleted!', 'success')
    return redirect(url_for('admin.manage_challenges'))

@admin_bp.route('/submissions')
@admin_required
def view_submissions():
    """
    Displays a list of all challenge submissions.
    Requires admin privileges.
    """
    submissions = Submission.query.order_by(Submission.timestamp.desc()).all()
    return render_template('admin/view_submissions.html', title='View Submissions', submissions=submissions)

@admin_bp.route('/users')
@admin_required
def manage_users():
    """
    Displays a list of all users for management.
    Requires admin privileges.
    """
    users = User.query.order_by(User.id.asc()).all()
    users_super_admin_status = {user.id: bool(user.is_super_admin) for user in users} # Ensure boolean
    return render_template('admin/manage_users.html', title='Manage Users', users=users, is_current_user_super_admin=bool(current_user.is_super_admin), users_super_admin_status=users_super_admin_status)

@admin_bp.route('/user/<int:user_id>/toggle_hidden', methods=['POST'])
@admin_required
def toggle_user_hidden(user_id):
    """
    Toggles the 'hidden' status of a user.

    Args:
        user_id (int): The ID of the user to modify.
    Requires admin privileges.
    """
    user = User.query.get_or_404(user_id)
    user.hidden = not user.hidden
    db.session.commit()
    flash(f'User {user.username} hidden status toggled to {user.hidden}.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/user/<int:user_id>/toggle_admin', methods=['POST'])
@admin_required
def toggle_user_admin(user_id):
    """
    Toggles the 'is_admin' status of a user. Only super admins can perform this action.

    Args:
        user_id (int): The ID of the user to modify.
    Requires admin privileges.
    """
    if not current_user.is_super_admin: # Only super admins can toggle admin status
        flash('You do not have permission to change admin status.', 'danger')
        return redirect(url_for('admin.manage_users'))

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot change your own admin status.', 'danger')
    elif user.is_super_admin and user.is_admin and not current_user.is_super_admin: # A super admin's admin status cannot be revoked by a non-super admin
        flash('You cannot revoke admin status from a Super Admin.', 'danger')
    elif user.is_super_admin and not current_user.is_super_admin: # A super admin's admin status cannot be changed by a non-super admin
        flash('Only Super Admins can manage other Super Admins\' status.', 'danger')
    else:
        user.is_admin = not user.is_admin
        # If a user is made admin, they should be hidden by default
        if user.is_admin:
            user.hidden = True
        db.session.commit()
        flash(f'User {user.username} admin status toggled to {user.is_admin}.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/profile/<username>/give_award_inline', methods=['POST'])
@admin_required
def give_award_to_user(username):
    """
    Handles giving an award to a specific user from their profile page.

    Args:
        username (str): The username of the recipient.
    Requires admin privileges.
    """
    target_user = User.query.filter_by(username=username).first_or_404()
    form = InlineGiveAwardForm()
    form.category.choices = [(ac.id, ac.name) for ac in AwardCategory.query.order_by(AwardCategory.name).all()]

    if form.validate_on_submit():
        award_category = AwardCategory.query.get(form.category.data)
        points_to_award = form.points.data

        if not award_category:
            flash('Invalid award category selected.', 'danger')
            return redirect(url_for('user_profile', username=username))

        # Create the award record
        award = Award(
            user_id=target_user.id,
            category_id=award_category.id,
            points_awarded=points_to_award,
            admin_id=current_user.id
        )
        db.session.add(award)

        # Update recipient's score
        target_user.score += points_to_award
        db.session.commit()

        flash(f'Award "{award_category.name}" with {points_to_award} points given to {target_user.username}!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('user_profile', username=username))

# Award Category CRUD
@admin_bp.route('/award_categories')
@admin_required
def manage_award_categories():
    """
    Displays a list of all award categories for management.
    Requires admin privileges.
    """
    award_categories = AwardCategory.query.all()
    return render_template('admin/manage_award_categories.html', title='Manage Award Categories', award_categories=award_categories)

@admin_bp.route('/award_category/new', methods=['GET', 'POST'])
@admin_required
def new_award_category():
    """
    Handles the creation of a new award category.
    Requires admin privileges.
    """
    form = AwardCategoryForm()
    if form.validate_on_submit():
        award_category = AwardCategory(name=form.name.data, default_points=form.default_points.data)
        db.session.add(award_category)
        db.session.commit()
        flash('Award Category has been created!', 'success')
        return redirect(url_for('admin.manage_award_categories'))
    return render_template('admin/create_award_category.html', title='New Award Category', form=form)

@admin_bp.route('/award_category/<int:category_id>/update', methods=['GET', 'POST'])
@admin_required
def update_award_category(category_id):
    """
    Handles the updating of an existing award category.

    Args:
        category_id (int): The ID of the award category to update.
    Requires admin privileges.
    """
    award_category = AwardCategory.query.get_or_404(category_id)
    form = AwardCategoryForm()
    if form.validate_on_submit():
        award_category.name = form.name.data
        award_category.default_points = form.default_points.data
        db.session.commit()
        flash('Award Category has been updated!', 'success')
        return redirect(url_for('admin.manage_award_categories'))
    elif request.method == 'GET':
        form.name.data = award_category.name
        form.default_points.data = award_category.default_points
    return render_template('admin/create_award_category.html', title='Update Award Category', form=form)

@admin_bp.route('/award_category/<int:category_id>/delete', methods=['POST'])
@admin_required
def delete_award_category(category_id):
    """
    Handles the deletion of an award category.

    Args:
        category_id (int): The ID of the award category to delete.
    Requires admin privileges.
    """
    award_category = AwardCategory.query.get_or_404(category_id)
    if award_category.awards: # Check if there are any awards associated with this category
        flash('Cannot delete category with associated awards. Please delete awards first.', 'danger')
        return redirect(url_for('admin.manage_award_categories'))
    db.session.delete(award_category)
    db.session.commit()
    flash('Award Category has been deleted!', 'success')
    return redirect(url_for('admin.manage_users'))

def _get_user_challenge_matrix_data():
    """
    Generates data for the User-Challenge Matrix Table.
    Returns all users, all challenges (ordered by solve count), and a map of user-challenge status.
    """
    all_users = User.query.order_by(User.score.desc()).all()
    
    challenges_by_solves = db.session.query(
        Challenge,
        func.count(Submission.id).label('solve_count')
    ).outerjoin(Submission, Challenge.id == Submission.challenge_id)\
     .group_by(Challenge.id)\
     .order_by(func.count(Submission.id).desc(), Challenge.name.asc())\
     .all()
    all_challenges = [c[0] for c in challenges_by_solves]

    solved_submissions = Submission.query.all()
    solved_map = {(s.user_id, s.challenge_id) for s in solved_submissions}

    unsuccessful_flag_attempts = FlagAttempt.query.filter_by(is_correct=False).all()
    unsuccessful_attempt_map = {(fa.user_id, fa.challenge_id) for fa in unsuccessful_flag_attempts}

    user_challenge_status = {}
    for user in all_users:
        user_challenge_status[user.id] = {}
        for challenge in all_challenges:
            if (user.id, challenge.id) in solved_map:
                user_challenge_status[user.id][challenge.id] = 'solved'
            elif (user.id, challenge.id) in unsuccessful_attempt_map:
                user_challenge_status[user.id][challenge.id] = 'attempted'
            else:
                user_challenge_status[user.id][challenge.id] = 'none'
    
    return all_users, all_challenges, user_challenge_status

def _get_challenge_solve_counts():
    """
    Calculates and returns the solve counts for each challenge.
    """
    return db.session.query(
        Challenge.name,
        func.count(Submission.id)
    ).join(Submission, Challenge.id == Submission.challenge_id).group_by(Challenge.name).order_by(func.count(Submission.id).desc()).all()

def _get_fails_vs_succeeds_data():
    """
    Calculates and returns the total successful and failed flag attempts.
    """
    total_successful_flag_attempts = db.session.query(func.count(FlagAttempt.id)).filter_by(is_correct=True).scalar()
    total_failed_flag_attempts = db.session.query(func.count(FlagAttempt.id)).filter_by(is_correct=False).scalar()
    return total_successful_flag_attempts, total_failed_flag_attempts

def _get_challenges_solved_over_time():
    """
    Calculates and returns the count of challenges solved over time, grouped by date.
    """
    return db.session.query(
        func.date(Submission.timestamp),
        func.count(Submission.id)
    ).group_by(func.date(Submission.timestamp)).order_by(func.date(Submission.timestamp)).all()

def _get_award_points_by_user():
    """
    Calculates and returns award points aggregated by user.
    """
    return db.session.query(
        User.username,
        func.sum(Award.points_awarded)
    ).join(Award, User.id == Award.user_id).group_by(User.username).all()

def _get_challenge_points_by_user():
    """
    Calculates and returns challenge points aggregated by user.
    """
    return db.session.query(
        User.username,
        func.sum(Submission.score_at_submission)
    ).join(Submission).group_by(User.username).all()

def _get_award_points_by_category():
    """
    Calculates and returns total award points.
    """
    return db.session.query(
        func.sum(Award.points_awarded)
    ).scalar()

def _get_challenge_points_by_category():
    """
    Calculates and returns challenge points aggregated by category.
    """
    return db.session.query(
        Category.name,
        func.sum(Submission.score_at_submission)
    ).join(Challenge, Category.id == Challenge.category_id).join(Submission, Challenge.id == Submission.challenge_id).group_by(Category.name).all()

@admin_bp.route('/analytics')
@admin_required
def analytics():
    """
    Displays various analytics and statistics for the platform.
    Requires admin privileges.
    """
    # Data for Points by Category
    challenge_points_by_category = _get_challenge_points_by_category()
    total_award_points = _get_award_points_by_category()
    
    category_data = {name: points for name, points in challenge_points_by_category}
    if total_award_points:
        category_data['Awards'] = category_data.get('Awards', 0) + total_award_points

    category_labels = list(category_data.keys())
    category_values = list(category_data.values())

    # Data for Points by User
    challenge_points_by_user = _get_challenge_points_by_user()
    award_points_by_user = _get_award_points_by_user()

    user_data = {username: points for username, points in challenge_points_by_user}
    for username, points in award_points_by_user:
        user_data[username] = user_data.get(username, 0) + points
    
    user_labels = list(user_data.keys())
    user_values = list(user_data.values())

    # Data for Challenges Solved Over Time
    challenges_solved_over_time = _get_challenges_solved_over_time()
    solved_dates = [str(date) for date, _ in challenges_solved_over_time]
    solved_counts = [count for _, count in challenges_solved_over_time]

    # Data for Challenge Points Over Time Chart (Cumulative Score)
    from scripts.chart_data_utils import get_global_score_history_data
    global_chart_data = get_global_score_history_data()

    if global_chart_data:
        global_stats_over_time = global_chart_data.get('global_stats_over_time', [])
        user_scores_over_time = global_chart_data.get('user_scores_over_time', {})
    else:
        global_stats_over_time = []
        user_scores_over_time = {}

    cumulative_points_dates = [item['x'] for item in global_stats_over_time]
    cumulative_points_values = [item['avg'] for item in global_stats_over_time]

    # Data for Fails vs Succeeds
    total_successful_flag_attempts, total_failed_flag_attempts = _get_fails_vs_succeeds_data()
    fails_succeeds_labels = ['Succeeds', 'Fails']
    fails_succeeds_values = [total_successful_flag_attempts, total_failed_flag_attempts]

    # Data for Challenges Solved Count (for bar graph)
    challenge_solve_counts = _get_challenge_solve_counts()
    challenge_solve_labels = [name for name, count in challenge_solve_counts]
    challenge_solve_values = [count for name, count in challenge_solve_counts]

    # Data for User-Challenge Matrix Table
    all_users, all_challenges, user_challenge_status = _get_user_challenge_matrix_data()

    return render_template('admin/analytics.html', 
                           title='Admin Analytics',
                           category_labels=category_labels,
                           category_values=category_values,
                           user_labels=user_labels,
                           user_values=user_values,
                           solved_dates=solved_dates,
                           solved_counts=solved_counts,
                           fails_succeeds_labels=fails_succeeds_labels,
                           fails_succeeds_values=fails_succeeds_values,
                           challenge_solve_labels=challenge_solve_labels,
                           challenge_solve_values=challenge_solve_values,
                           cumulative_points_dates=cumulative_points_dates,
                           cumulative_points_values=cumulative_points_values,
                           all_users=all_users,
                           all_challenges=all_challenges,
                           user_challenge_status=user_challenge_status)