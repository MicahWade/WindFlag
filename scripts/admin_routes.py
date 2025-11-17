from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from scripts.extensions import db
from scripts.models import Category, Challenge, Submission, User
from scripts.forms import CategoryForm, ChallengeForm # These forms will be created later
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
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        challenge = Challenge(name=form.name.data, description=form.description.data,
                              points=form.points.data, flag=form.flag.data,
                              category_id=form.category.data)
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
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        challenge.name = form.name.data
        challenge.description = form.description.data
        challenge.points = form.points.data
        challenge.flag = form.flag.data
        challenge.category_id = form.category.data
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
