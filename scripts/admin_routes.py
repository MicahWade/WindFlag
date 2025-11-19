from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from scripts.extensions import db, get_setting
from scripts.models import Category, Challenge, Submission, User, Setting, ChallengeFlag, FlagSubmission, AwardCategory, Award, FlagAttempt # Import FlagAttempt
from scripts.forms import CategoryForm, ChallengeForm, AdminSettingsForm, AwardCategoryForm, InlineGiveAwardForm
from functools import wraps
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
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
    return render_template('admin/index.html', title='Admin Dashboard')

@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    form = AdminSettingsForm()
    if form.validate_on_submit():
        # Save TOP_X_SCOREBOARD setting
        top_x_val = str(form.top_x_scoreboard.data)
        setting_top_x = Setting.query.filter_by(key='TOP_X_SCOREBOARD').first()
        if setting_top_x:
            setting_top_x.value = top_x_val
        else:
            setting_top_x = Setting(key='TOP_X_SCOREBOARD', value=top_x_val)
            db.session.add(setting_top_x)

        # Save SCOREBOARD_GRAPH_TYPE setting
        graph_type_val = form.scoreboard_graph_type.data
        setting_graph_type = Setting.query.filter_by(key='SCOREBOARD_GRAPH_TYPE').first()
        if setting_graph_type:
            setting_graph_type.value = graph_type_val
        else:
            setting_graph_type = Setting(key='SCOREBOARD_GRAPH_TYPE', value=graph_type_val)
            db.session.add(setting_graph_type)

        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.admin_settings'))
    elif request.method == 'GET':
        form.top_x_scoreboard.data = int(get_setting('TOP_X_SCOREBOARD', '10'))
        form.scoreboard_graph_type.data = get_setting('SCOREBOARD_GRAPH_TYPE', 'line')
    return render_template('admin/settings.html', title='Admin Settings', form=form)

# Category CRUD
@admin_bp.route('/categories')
@admin_required
def manage_categories():
    categories = Category.query.all()
    return render_template('admin/manage_categories.html', title='Manage Categories', categories=categories)

@admin_bp.route('/category/new', methods=['GET', 'POST'])
@admin_required
def new_category():
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
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category has been deleted!', 'success')
    return redirect(url_for('admin.manage_categories'))

# Challenge CRUD
@admin_bp.route('/challenges')
@admin_required
def manage_challenges():
    challenges = Challenge.query.all()
    return render_template('admin/manage_challenges.html', title='Manage Challenges', challenges=challenges)

@admin_bp.route('/challenge/new', methods=['GET', 'POST'])
@admin_required
def new_challenge():
    form = ChallengeForm()
    form.category.choices.extend([(c.id, c.name) for c in Category.query.all()])
    if form.validate_on_submit():
        category_id = None
        if form.new_category_name.data:
            new_category = Category(name=form.new_category_name.data)
            db.session.add(new_category)
            db.session.commit()
            category_id = new_category.id
        else:
            category_id = form.category.data

        challenge = Challenge(name=form.name.data, description=form.description.data,
                              points=form.points.data,
                              case_sensitive=form.case_sensitive.data,
                              category_id=category_id,
                              multi_flag_type=form.multi_flag_type.data,
                              multi_flag_threshold=form.multi_flag_threshold.data if form.multi_flag_type.data == 'N_OF_M' else None)
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
    return render_template('admin/create_challenge.html', title='New Challenge', form=form)

@admin_bp.route('/challenge/<int:challenge_id>/update', methods=['GET', 'POST'])
@admin_required
def update_challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    form = ChallengeForm()
    form.category.choices.extend([(c.id, c.name) for c in Category.query.all()])
    if form.validate_on_submit():
        category_id = None
        if form.new_category_name.data:
            new_category = Category(name=form.new_category_name.data)
            db.session.add(new_category)
            db.session.commit()
            category_id = new_category.id
        else:
            category_id = form.category.data

        challenge.name = form.name.data
        challenge.description = form.description.data
        challenge.points = form.points.data
        challenge.case_sensitive = form.case_sensitive.data
        challenge.category_id = category_id
        challenge.multi_flag_type = form.multi_flag_type.data
        challenge.multi_flag_threshold = form.multi_flag_threshold.data if form.multi_flag_type.data == 'N_OF_M' else None
        
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
        # form.flag.data = challenge.flag # Removed
        form.case_sensitive.data = challenge.case_sensitive
        form.category.data = challenge.category_id
        form.multi_flag_type.data = challenge.multi_flag_type
        form.multi_flag_threshold.data = challenge.multi_flag_threshold
        form.flags_input.data = "\n".join([f.flag_content for f in challenge.flags])

    return render_template('admin/create_challenge.html', title='Update Challenge', form=form)

@admin_bp.route('/challenge/<int:challenge_id>/delete', methods=['POST'])
@admin_required
def delete_challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    db.session.delete(challenge)
    db.session.commit()
    flash('Challenge has been deleted!', 'success')
    return redirect(url_for('admin.manage_challenges'))

@admin_bp.route('/submissions')
@admin_required
def view_submissions():
    submissions = Submission.query.order_by(Submission.timestamp.desc()).all()
    return render_template('admin/view_submissions.html', title='View Submissions', submissions=submissions)

@admin_bp.route('/users')
@admin_required
def manage_users():
    users = User.query.order_by(User.id.asc()).all()
    return render_template('admin/manage_users.html', title='Manage Users', users=users)

@admin_bp.route('/user/<int:user_id>/toggle_hidden', methods=['POST'])
@admin_required
def toggle_user_hidden(user_id):
    user = User.query.get_or_404(user_id)
    user.hidden = not user.hidden
    db.session.commit()
    flash(f'User {user.username} hidden status toggled to {user.hidden}.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/user/<int:user_id>/toggle_admin', methods=['POST'])
@admin_required
def toggle_user_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot change your own admin status.', 'danger')
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
    award_categories = AwardCategory.query.all()
    return render_template('admin/manage_award_categories.html', title='Manage Award Categories', award_categories=award_categories)

@admin_bp.route('/award_category/new', methods=['GET', 'POST'])
@admin_required
def new_award_category():
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
    award_category = AwardCategory.query.get_or_404(category_id)
    if award_category.awards: # Check if there are any awards associated with this category
        flash('Cannot delete category with associated awards. Please delete awards first.', 'danger')
        return redirect(url_for('admin.manage_award_categories'))
    db.session.delete(award_category)
    db.session.commit()
    flash('Award Category has been deleted!', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/analytics')
@admin_required
def analytics():
    # Data for Points by Category
    # 1. Challenge points by category
    challenge_points_by_category = db.session.query(
        Category.name,
        func.sum(Submission.score_at_submission)
    ).join(Challenge, Category.id == Challenge.category_id).join(Submission, Challenge.id == Submission.challenge_id).group_by(Category.name).all()

    # 2. Award points (aggregated into a single 'Awards' category)
    total_award_points = db.session.query(
        func.sum(Award.points_awarded)
    ).scalar()
    
    category_data = {name: points for name, points in challenge_points_by_category}
    if total_award_points:
        category_data['Awards'] = category_data.get('Awards', 0) + total_award_points

    category_labels = list(category_data.keys())
    category_values = list(category_data.values())

    # Data for Points by User
    # 1. Challenge points by user
    challenge_points_by_user = db.session.query(
        User.username,
        func.sum(Submission.score_at_submission)
    ).join(Submission).group_by(User.username).all()

    # 2. Award points by user
    award_points_by_user = db.session.query(
        User.username,
        func.sum(Award.points_awarded)
    ).join(Award, User.id == Award.user_id).group_by(User.username).all()

    user_data = {username: points for username, points in challenge_points_by_user}
    for username, points in award_points_by_user:
        user_data[username] = user_data.get(username, 0) + points
    
    user_labels = list(user_data.keys())
    user_values = list(user_data.values())

    # Data for Challenges Solved Over Time
    # Group submissions by date and count them
    challenges_solved_over_time = db.session.query(
        func.date(Submission.timestamp),
        func.count(Submission.id)
    ).group_by(func.date(Submission.timestamp)).order_by(func.date(Submission.timestamp)).all()

    solved_dates = [str(date) for date, _ in challenges_solved_over_time]
    solved_counts = [count for _, count in challenges_solved_over_time]

    # Data for Challenge Points Over Time Chart (Cumulative Score)
    # Get all submissions ordered by timestamp
    all_submissions_ordered = Submission.query.order_by(Submission.timestamp).all()

    cumulative_scores = {}
    current_cumulative_score = 0
    
    for submission in all_submissions_ordered:
        # Assuming score_at_submission is the score of the challenge itself
        # For cumulative, we need to sum up points of solved challenges
        # This requires re-calculating cumulative score based on challenge points
        # Or, if score_at_submission is already cumulative, use that.
        # Let's assume score_at_submission is the score of the challenge itself,
        # and we need to sum it up.
        
        # Find the challenge to get its points
        challenge_points = Challenge.query.get(submission.challenge_id).points
        current_cumulative_score += challenge_points
        
        date_key = submission.timestamp.strftime('%Y-%m-%d')
        cumulative_scores[date_key] = current_cumulative_score # Store the latest cumulative score for this date

    # Convert to lists for Chart.js
    cumulative_points_dates = sorted(cumulative_scores.keys())
    cumulative_points_values = [cumulative_scores[date] for date in cumulative_points_dates]

    # Data for Fails vs Succeeds
    total_successful_flag_attempts = db.session.query(func.count(FlagAttempt.id)).filter_by(is_correct=True).scalar()
    total_failed_flag_attempts = db.session.query(func.count(FlagAttempt.id)).filter_by(is_correct=False).scalar()

    fails_succeeds_labels = ['Succeeds', 'Fails']
    fails_succeeds_values = [total_successful_flag_attempts, total_failed_flag_attempts]

    # Data for Challenges Solved Count (for bar graph)
    challenge_solve_counts = db.session.query(
        Challenge.name,
        func.count(Submission.id)
    ).join(Submission, Challenge.id == Submission.challenge_id).group_by(Challenge.name).order_by(func.count(Submission.id).desc()).all()

    challenge_solve_labels = [name for name, count in challenge_solve_counts]
    challenge_solve_values = [count for name, count in challenge_solve_counts]

    # Data for User-Challenge Matrix Table
    all_users = User.query.order_by(User.score.desc()).all()
    # Order challenges by most solves
    challenges_by_solves = db.session.query(
        Challenge,
        func.count(Submission.id).label('solve_count')
    ).outerjoin(Submission, Challenge.id == Submission.challenge_id)\
     .group_by(Challenge.id)\
     .order_by(func.count(Submission.id).desc(), Challenge.name.asc())\
     .all()
    all_challenges = [c[0] for c in challenges_by_solves]

    # Get all successful submissions
    solved_submissions = Submission.query.all()
    solved_map = {(s.user_id, s.challenge_id) for s in solved_submissions}

    # Get all flag attempts that were unsuccessful
    unsuccessful_flag_attempts = FlagAttempt.query.filter_by(is_correct=False).all()
    unsuccessful_attempt_map = {(fa.user_id, fa.challenge_id) for fa in unsuccessful_flag_attempts}

    # Build the matrix
    user_challenge_status = {} # {user_id: {challenge_id: 'solved'/'attempted'/'none'}}

    for user in all_users:
        user_challenge_status[user.id] = {}
        for challenge in all_challenges:
            if (user.id, challenge.id) in solved_map:
                user_challenge_status[user.id][challenge.id] = 'solved'
            elif (user.id, challenge.id) in unsuccessful_attempt_map:
                # Only mark as 'attempted' if not already 'solved'
                user_challenge_status[user.id][challenge.id] = 'attempted'
            else:
                user_challenge_status[user.id][challenge.id] = 'none'

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