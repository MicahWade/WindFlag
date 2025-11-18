from datetime import datetime, UTC
from .extensions import db, login_manager
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM # For PostgreSQL, if needed, but using String for now

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    hidden = db.Column(db.Boolean, nullable=False, default=False)
    last_seen = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    score = db.Column(db.Integer, nullable=False, default=0)
    submissions = db.relationship('Submission', backref='solver', lazy=True)
    # Modified: Use back_populates for clarity and to resolve SAWarning
    flag_submissions = db.relationship('FlagSubmission', back_populates='user_rel', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    challenges = db.relationship('Challenge', backref='category', lazy=True)

    def __repr__(self):
        return f"Category('{self.name}')"

# Define Multi-Flag Types
MULTI_FLAG_TYPES = ('SINGLE', 'ANY', 'ALL', 'N_OF_M')

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    # Removed 'flag' column
    case_sensitive = db.Column(db.Boolean, nullable=False, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    submissions = db.relationship('Submission', back_populates='challenge_rel', lazy=True, primaryjoin="Challenge.id == Submission.challenge_id")
    
    # New fields for multi-flag challenges
    multi_flag_type = db.Column(db.String(10), nullable=False, default='SINGLE') # e.g., 'SINGLE', 'ANY', 'ALL', 'N_OF_M'
    multi_flag_threshold = db.Column(db.Integer, nullable=True) # For 'N_OF_M' type, stores N
    
    flags = db.relationship('ChallengeFlag', backref='challenge', lazy=True, cascade="all, delete-orphan") # New relationship

    def __repr__(self):
        return f"Challenge('{self.name}', '{self.points}', Type: '{self.multi_flag_type}')"

class ChallengeFlag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    flag_content = db.Column(db.String(100), nullable=False)
    # Optional: order = db.Column(db.Integer, nullable=True) # If flags need a specific order

    def __repr__(self):
        return f"ChallengeFlag(Challenge ID: {self.challenge_id}, Flag: '{self.flag_content}')"

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    score_at_submission = db.Column(db.Integer, nullable=False)

    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    # Modify explicit relationship to Challenge to use back_populates
    challenge_rel = db.relationship('Challenge', back_populates='submissions')

    def __repr__(self):
        return f"Submission('{self.user_id}', '{self.challenge_id}', '{self.timestamp}')"

class FlagSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    challenge_flag_id = db.Column(db.Integer, db.ForeignKey('challenge_flag.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))

    # Modified: Use back_populates for clarity and to resolve SAWarning
    user_rel = db.relationship('User', back_populates='flag_submissions')
    # Modified: Use distinct backref names to avoid conflicts
    challenge = db.relationship('Challenge', backref='flag_submissions_for_challenge', foreign_keys=[challenge_id])
    challenge_flag = db.relationship('ChallengeFlag', backref='flag_submissions_for_flag', foreign_keys=[challenge_flag_id])

    def __repr__(self):
        return f"FlagSubmission(User: {self.user_id}, Challenge: {self.challenge_id}, Flag: {self.challenge_flag_id})"

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f"Setting('{self.key}', '{self.value}')"
