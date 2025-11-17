from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required
from scripts.config import Config
from scripts.forms import RegistrationForm, LoginForm, FlagSubmissionForm # Import forms
from datetime import datetime # Import datetime
from sqlalchemy import func # Import func for aggregation
from scripts.extensions import db, login_manager, bcrypt # Import extensions
from scripts.admin_routes import admin_bp # Import admin blueprint
import sys # Import sys

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
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
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
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
    def challenges():
        categories = Category.query.all()
        flag_form = FlagSubmissionForm() # Instantiate the form
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
                    flash('You have already solved this challenge!', 'info')
                else:
                    new_submission = Submission(user_id=current_user.id, challenge_id=challenge.id, timestamp=datetime.utcnow())
                    db.session.add(new_submission)
                    db.session.commit()
                    flash('Correct Flag! You earned points!', 'success')
            else:
                flash('Incorrect Flag. Please try again.', 'danger')
        return redirect(url_for('challenges'))

    @app.route('/scoreboard')
    def scoreboard():
        # Query users and their total scores
        # Order by score (descending), then by last submission timestamp (ascending)
        scoreboard_data = db.session.query(
            User.username,
            func.sum(Challenge.points).label('score'),
            func.max(Submission.timestamp).label('last_submission')
        ).join(Submission, User.id == Submission.user_id)\
         .join(Challenge, Submission.challenge_id == Challenge.id)\
         .group_by(User.id)\
         .order_by(func.sum(Challenge.points).desc(), func.max(Submission.timestamp).asc())\
         .all()
        return render_template('scoreboard.html', title='Scoreboard', scoreboard_data=scoreboard_data)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
