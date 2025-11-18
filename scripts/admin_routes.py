from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app # Import current_app
from flask_login import login_required, current_user
from scripts.extensions import db, get_setting # Import get_setting
from scripts.models import Category, Challenge, Submission, User, Setting # Import Setting
from scripts.forms import CategoryForm, ChallengeForm, AdminSettingsForm # Import AdminSettingsForm
from functools import wraps # Import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f) # Add wraps decorator
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
        form.top_x_scoreboard.data = int(get_setting('TOP_X_SCOREBOARD', '10')) # Default to 10
        form.scoreboard_graph_type.data = get_setting('SCOREBOARD_GRAPH_TYPE', 'line') # Default to 'line'
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
                              points=form.points.data, flag=form.flag.data,
                              category_id=category_id)
        db.session.add(challenge)
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
        challenge.flag = form.flag.data
        challenge.category_id = category_id
        db.session.commit()
        flash('Challenge has been updated!', 'success')
        return redirect(url_for('admin.manage_challenges'))
    elif request.method == 'GET':
        form.name.data = challenge.name
        form.description.data = challenge.description
        form.points.data = challenge.points
        form.flag.data = challenge.flag
        form.category.data = challenge.category_id
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
