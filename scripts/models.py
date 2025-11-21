"""
SQLAlchemy models for the WindFlag CTF platform.

This module defines the database schema for users, challenges, submissions,
awards, and other related entities.
"""
from datetime import datetime, UTC
from .extensions import db, login_manager
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM # For PostgreSQL, if needed, but using String for now

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """
    Represents a user in the CTF platform.

    Attributes:
        id (int): Primary key.
        username (str): Unique username.
        email (str): Unique email address (optional).
        password_hash (str): Hashed password.
        is_admin (bool): True if the user has admin privileges.
        is_super_admin (bool): True if the user has super admin privileges.
        hidden (bool): True if the user's profile should be hidden from public view.
        last_seen (datetime): Timestamp of the user's last activity.
        score (int): Current score of the user.
        submissions (relationship): One-to-many relationship with Submission.
        flag_submissions (relationship): One-to-many relationship with FlagSubmission.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_super_admin = db.Column(db.Boolean, nullable=False, default=False)
    hidden = db.Column(db.Boolean, nullable=False, default=False)
    last_seen = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    score = db.Column(db.Integer, nullable=False, default=0)
    submissions = db.relationship('Submission', backref='solver', lazy=True)
    # Modified: Use back_populates for clarity and to resolve SAWarning
    flag_submissions = db.relationship('FlagSubmission', back_populates='user_rel', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Category(db.Model):
    """
    Represents a category for challenges.

    Attributes:
        id (int): Primary key.
        name (str): Unique name of the category.
        challenges (relationship): One-to-many relationship with Challenge.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    challenges = db.relationship('Challenge', backref='category', lazy=True)

    def __repr__(self):
        return f"Category('{self.name}')"

# Define Multi-Flag Types
MULTI_FLAG_TYPES = ('SINGLE', 'ANY', 'ALL', 'N_OF_M')

class Challenge(db.Model):
    """
    Represents a challenge in the CTF platform.

    Attributes:
        id (int): Primary key.
        name (str): Unique name of the challenge.
        description (str): Description of the challenge.
        points (int): Points awarded for solving the challenge.
        hint_cost (int): Cost in points to reveal a hint for this challenge.
        case_sensitive (bool): True if the flag submission is case-sensitive.
        category_id (int): Foreign key to the Category model.
        submissions (relationship): One-to-many relationship with Submission.
        multi_flag_type (str): Type of multi-flag challenge ('SINGLE', 'ANY', 'ALL', 'N_OF_M').
        multi_flag_threshold (int): For 'N_OF_M' type, the number of flags required.
        flags (relationship): One-to-many relationship with ChallengeFlag.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    hint_cost = db.Column(db.Integer, nullable=False, default=0)
    case_sensitive = db.Column(db.Boolean, nullable=False, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    submissions = db.relationship('Submission', back_populates='challenge_rel', lazy=True, primaryjoin="Challenge.id == Submission.challenge_id")
    multi_flag_type = db.Column(db.String(10), nullable=False, default='SINGLE') # e.g., 'SINGLE', 'ANY', 'ALL', 'N_OF_M'
    multi_flag_threshold = db.Column(db.Integer, nullable=True) # For 'N_OF_M' type, stores N
    
    flags = db.relationship('ChallengeFlag', backref='challenge', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Challenge('{self.name}', '{self.points}', Type: '{self.multi_flag_type}')"

class ChallengeFlag(db.Model):
    """
    Represents a flag for a challenge. A challenge can have multiple flags.

    Attributes:
        id (int): Primary key.
        challenge_id (int): Foreign key to the Challenge model.
        flag_content (str): The actual flag string.
    """
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    flag_content = db.Column(db.String(100), nullable=False)


    def __repr__(self):
        return f"ChallengeFlag(Challenge ID: {self.challenge_id}, Flag: '{self.flag_content}')"

class Submission(db.Model):
    """
    Records a successful submission of a challenge by a user.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to the User model (solver).
        timestamp (datetime): The time of the submission.
        score_at_submission (int): The user's score at the time of this submission.
        challenge_id (int): Foreign key to the Challenge model.
        challenge_rel (relationship): Many-to-one relationship with Challenge.
    """
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
    """
    Records a successful submission of a specific flag for a challenge by a user.
    This is used for multi-flag challenges.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to the User model.
        challenge_id (int): Foreign key to the Challenge model.
        challenge_flag_id (int): Foreign key to the ChallengeFlag model.
        timestamp (datetime): The time of the flag submission.
        user_rel (relationship): Many-to-one relationship with User.
        challenge (relationship): Many-to-one relationship with Challenge.
        challenge_flag (relationship): Many-to-one relationship with ChallengeFlag.
    """
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

class FlagAttempt(db.Model):
    """
    Records every attempt (correct or incorrect) to submit a flag for a challenge.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to the User model.
        challenge_id (int): Foreign key to the Challenge model.
        submitted_flag (str): The content of the flag submitted by the user.
        is_correct (bool): True if the submitted flag was correct, False otherwise.
        timestamp (datetime): The time of the attempt.
        user (relationship): Many-to-one relationship with User.
        challenge (relationship): Many-to-one relationship with Challenge.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    submitted_flag = db.Column(db.String(256), nullable=False) # Store the actual submitted flag
    is_correct = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))

    user = db.relationship('User', backref='flag_attempts')
    challenge = db.relationship('Challenge', backref='flag_attempts_for_challenge')

    def __repr__(self):
        return f"FlagAttempt(User: {self.user_id}, Challenge: {self.challenge_id}, Correct: {self.is_correct})"

class Setting(db.Model):
    """
    Stores application-wide settings as key-value pairs.

    Attributes:
        id (int): Primary key.
        key (str): Unique key for the setting.
        value (str): Value of the setting.
    """
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f"Setting('{self.key}', '{self.value}')"

class AwardCategory(db.Model):
    """
    Defines categories for awards that can be given to users.

    Attributes:
        id (int): Primary key.
        name (str): Unique name of the award category.
        default_points (int): Default points awarded for this category.
        awards (relationship): One-to-many relationship with Award.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    default_points = db.Column(db.Integer, nullable=False, default=0)
    awards = db.relationship('Award', backref='category', lazy=True)

    def __repr__(self):
        return f"AwardCategory('{self.name}', Points: {self.default_points})"

class Award(db.Model):
    """
    Records an award given to a user.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to the User model (recipient).
        category_id (int): Foreign key to the AwardCategory model.
        points_awarded (int): Points given with this award.
        admin_id (int): Foreign key to the User model (admin who gave the award).
        timestamp (datetime): The time the award was given.
        recipient (relationship): Many-to-one relationship with User (recipient).
        giver (relationship): Many-to-one relationship with User (giver).
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # User receiving the award
    category_id = db.Column(db.Integer, db.ForeignKey('award_category.id'), nullable=False)
    points_awarded = db.Column(db.Integer, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Admin giving the award
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))

    # Relationships
    recipient = db.relationship('User', foreign_keys=[user_id], backref='awards_received')
    giver = db.relationship('User', foreign_keys=[admin_id], backref='awards_given')

    def __repr__(self):
        return f"Award(Recipient: {self.user_id}, Category: {self.category_id}, Points: {self.points_awarded}, Giver: {self.admin_id})"

class Hint(db.Model):
    """
    Represents a hint for a challenge.

    Attributes:
        id (int): Primary key.
        challenge_id (int): Foreign key to the Challenge model.
        title (str): Title of the hint.
        content (str): The content of the hint.
        cost (int): Points deducted from the user for revealing this hint.
        challenge (relationship): Many-to-one relationship with Challenge.
    """
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False, default="Hint")
    content = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Integer, nullable=False, default=0)
    challenge = db.relationship('Challenge', backref='hints', lazy=True)

    def __repr__(self):
        return f"Hint(Challenge ID: {self.challenge_id}, Cost: {self.cost})"

class UserHint(db.Model):
    """
    Records which hints a user has revealed.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to the User model.
        hint_id (int): Foreign key to the Hint model.
        timestamp (datetime): The time the hint was revealed.
        user (relationship): Many-to-one relationship with User.
        hint (relationship): Many-to-one relationship with Hint.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hint_id = db.Column(db.Integer, db.ForeignKey('hint.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))

    user = db.relationship('User', backref='revealed_hints', lazy=True)
    hint = db.relationship('Hint', backref='revealed_by_users', lazy=True)

    # Ensure a user can only reveal a specific hint once
    __table_args__ = (db.UniqueConstraint('user_id', 'hint_id', name='_user_hint_uc'),)

    def __repr__(self):
        return f"UserHint(User: {self.user_id}, Hint: {self.hint_id})"


