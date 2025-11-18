from datetime import datetime
from .extensions import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False) # Added is_admin field
    hidden = db.Column(db.Boolean, nullable=False, default=False) # Added hidden field
    last_seen = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # Added last_seen field
    score = db.Column(db.Integer, nullable=False, default=0) # New score column
    submissions = db.relationship('Submission', backref='solver', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    challenges = db.relationship('Challenge', backref='category', lazy=True)

    def __repr__(self):
        return f"Category('{self.name}')"

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    flag = db.Column(db.String(100), nullable=False)
    case_sensitive = db.Column(db.Boolean, nullable=False, default=True) # New field
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    submissions = db.relationship('Submission', backref='challenge_solved', lazy=True)

    def __repr__(self):
        return f"Challenge('{self.name}', '{self.points}')"

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    score_at_submission = db.Column(db.Integer, nullable=False) # New column to store score at the time of submission

    def __repr__(self):
        return f"Submission('{self.user_id}', '{self.challenge_id}', '{self.timestamp}')"

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f"Setting('{self.key}', '{self.value}')"
