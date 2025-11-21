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
POINT_DECAY_TYPES = ('STATIC', 'LINEAR', 'LOGARITHMIC')
UNLOCK_TYPES = ('NONE', 'PREREQUISITE_PERCENTAGE', 'PREREQUISITE_COUNT', 'TIMED', 'COMBINED')
UNLOCK_POINT_REDUCTION_TYPES = ('NONE', 'FIXED', 'PERCENTAGE', 'TIME_DECAY_TO_ZERO')

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
        point_decay_type (str): Type of point decay ('STATIC', 'LINEAR', 'LOGARITHMIC').
        point_decay_rate (int): Rate of point decay.
        proactive_decay (bool): True if points decay proactively.
        minimum_points (int): Minimum points a challenge can decay to.
        unlock_type (str): Type of unlocking mechanism ('NONE', 'PREREQUISITE_PERCENTAGE', 'PREREQUISITE_COUNT', 'PREREQUISITE_CHALLENGES', 'TIMED', 'COMBINED').
        prerequisite_percentage_value (int): Percentage of challenges to complete for unlocking.
        prerequisite_count_value (int): Number of challenges to complete for unlocking.
        prerequisite_challenge_ids (list): List of specific challenge IDs that must be completed for unlocking.
        unlock_date_time (datetime): Specific date and time for timed unlocking.
        unlock_point_reduction_type (str): Type of point reduction upon unlocking ('NONE', 'FIXED', 'PERCENTAGE', 'TIME_DECAY_TO_ZERO').
        unlock_point_reduction_value (int): Value for fixed or percentage point reduction.
        unlock_point_reduction_target_date (datetime): Target date for time-decay to zero point reduction.
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
    multi_flag_threshold = db.Column(db.Integer, nullable=True) # For 'N_of_M' type, stores N
    point_decay_type = db.Column(db.String(20), nullable=False, default='STATIC') # STATIC, LINEAR, LOGARITHMIC
    point_decay_rate = db.Column(db.Integer, nullable=True)
    proactive_decay = db.Column(db.Boolean, nullable=False, default=False)
    minimum_points = db.Column(db.Integer, nullable=False, default=1)
    
    # New fields for challenge unlocking and dynamic point adjustment
    unlock_type = db.Column(db.String(50), nullable=False, default='NONE')
    prerequisite_percentage_value = db.Column(db.Integer, nullable=True)
    prerequisite_count_value = db.Column(db.Integer, nullable=True)
    prerequisite_count_category_ids = db.Column(db.JSON, nullable=True) # New: Stores a list of category IDs for prerequisite count
    prerequisite_challenge_ids = db.Column(db.JSON, nullable=True) # Stores a list of challenge IDs
    unlock_date_time = db.Column(db.DateTime, nullable=True)
    
    unlock_point_reduction_type = db.Column(db.String(50), nullable=False, default='NONE')
    unlock_point_reduction_value = db.Column(db.Integer, nullable=True)
    unlock_point_reduction_target_date = db.Column(db.DateTime, nullable=True)
    is_hidden = db.Column(db.Boolean, nullable=False, default=False) # New: Field to hide challenge from non-admins
    
    flags = db.relationship('ChallengeFlag', backref='challenge', lazy=True, cascade="all, delete-orphan")

    @property
    def total_challenges(self):
        """Returns the total number of challenges in the system."""
        return Challenge.query.count()

    def get_user_completed_challenges(self, user):
        """Returns a set of challenge IDs completed by the given user."""
        if not user or not user.is_authenticated:
            return set()
        return {s.challenge_id for s in Submission.query.filter_by(user_id=user.id).all()}

    def is_unlocked_for_user(self, user):
        """
        Determines if the challenge is unlocked for the given user based on its unlock_type.
        """
        # Admins can always view challenges, regardless of unlock conditions.
        # This means for an admin, the challenge is always considered "unlocked" for display/management.
        if user and user.is_admin:
            return True

        # If the challenge is explicitly hidden, it's not unlocked for regular users
        if self.is_hidden:
            return False

        if self.unlock_type == 'NONE':
            return True

        unlocked_by_prerequisites = True
        unlocked_by_time = True

        user_completed_challenge_ids = self.get_user_completed_challenges(user)
        
        # Universal Prerequisite: Always check specific challenge prerequisites if they are set
        if self.prerequisite_challenge_ids:
            required_ids = set(self.prerequisite_challenge_ids)
            if not required_ids.issubset(user_completed_challenge_ids):
                unlocked_by_prerequisites = False

        # Only proceed with unlock_type specific checks if universal prerequisites are met
        if unlocked_by_prerequisites:
            all_challenges = Challenge.query.all()
            total_challenges_count = len(all_challenges)
            user_completed_challenges_count = len(user_completed_challenge_ids)

            # Check unlock_type specific conditions
            if self.unlock_type == 'PREREQUISITE_PERCENTAGE':
                if total_challenges_count > 0:
                    completed_percentage = (user_completed_challenges_count / total_challenges_count) * 100
                    if completed_percentage < (self.prerequisite_percentage_value or 0):
                        unlocked_by_prerequisites = False
                else: # No challenges in system, so percentage cannot be met
                    unlocked_by_prerequisites = False
            elif self.unlock_type == 'PREREQUISITE_COUNT':
                if self.prerequisite_count_category_ids:
                    # Filter completed challenges by specified categories
                    from scripts.models import Category # Import here to avoid circular dependency
                    target_category_ids = set(self.prerequisite_count_category_ids)
                    
                    # Get challenges that belong to the target categories
                    challenges_in_target_categories = Challenge.query.filter(Challenge.category_id.in_(list(target_category_ids))).all()
                    challenges_in_target_categories_ids = {c.id for c in challenges_in_target_categories}

                    # Count user's completed challenges that are also in the target categories
                    user_completed_in_target_categories_count = len(user_completed_challenge_ids.intersection(challenges_in_target_categories_ids))

                    if user_completed_in_target_categories_count < (self.prerequisite_count_value or 0):
                        unlocked_by_prerequisites = False
                else:
                    # If no specific categories are selected, use the total count of completed challenges
                    if user_completed_challenges_count < (self.prerequisite_count_value or 0):
                        unlocked_by_prerequisites = False
            elif self.unlock_type == 'PREREQUISITE_CHALLENGES':
                # This is now handled as a universal prerequisite above, so this block is effectively a no-op
                pass
            elif self.unlock_type == 'COMBINED':
                # For combined, check all relevant prerequisite types if they are set
                if self.prerequisite_percentage_value:
                    if total_challenges_count > 0:
                        completed_percentage = (user_completed_challenges_count / total_challenges_count) * 100
                        if completed_percentage < self.prerequisite_percentage_value:
                            unlocked_by_prerequisites = False
                    else:
                        unlocked_by_prerequisites = False
                
                if unlocked_by_prerequisites and self.prerequisite_count_value:
                    if self.prerequisite_count_category_ids:
                        from scripts.models import Category # Import here to avoid circular dependency
                        target_category_ids = set(self.prerequisite_count_category_ids)
                        challenges_in_target_categories = Challenge.query.filter(Challenge.category_id.in_(list(target_category_ids))).all()
                        challenges_in_target_categories_ids = {c.id for c in challenges_in_target_categories}
                        user_completed_in_target_categories_count = len(user_completed_challenge_ids.intersection(challenges_in_target_categories_ids))
                        if user_completed_in_target_categories_count < (self.prerequisite_count_value or 0):
                            unlocked_by_prerequisites = False
                    else:
                        if user_completed_challenges_count < (self.prerequisite_count_value or 0):
                            unlocked_by_prerequisites = False
                # Specific challenge prerequisites are handled universally at the top

        # Check time-based conditions
        if self.unlock_type in ['TIMED', 'COMBINED']:
            if self.unlock_date_time and datetime.now(UTC) < self.unlock_date_time:
                unlocked_by_time = False

        if self.unlock_type == 'COMBINED':
            return unlocked_by_prerequisites and unlocked_by_time
        elif self.unlock_type == 'TIMED':
            return unlocked_by_time
        else: # PREREQUISITE_PERCENTAGE, PREREQUISITE_COUNT, PREREQUISITE_CHALLENGES (now handled universally)
            return unlocked_by_prerequisites

    def get_unlocked_percentage_for_eligible_users(self):
        """
        Calculates the percentage of eligible users (non-admin, non-hidden)
        for whom this challenge is currently unlocked.
        """
        # Import User model here to avoid circular dependency at module level
        from scripts.models import User 

        eligible_users = User.query.filter_by(is_admin=False, hidden=False).all()
        if not eligible_users:
            return 0.0

        unlocked_count = 0
        for user in eligible_users:
            # Temporarily override is_hidden check for this calculation
            # We want to know if it's unlocked *if it weren't explicitly hidden*
            # This is a bit tricky. The `is_unlocked_for_user` method already
            # checks `is_hidden`. If `is_hidden` is True, it will return False.
            # For this specific calculation, we want to know if the *prerequisites*
            # are met, regardless of the `is_hidden` flag itself.
            # A simpler approach is to check the unlock conditions directly,
            # or to pass a flag to `is_unlocked_for_user`.
            
            # Let's refine: `is_unlocked_for_user` should be used as is,
            # because if a challenge is `is_hidden=True`, it's not "unlocked"
            # for any regular user, and thus shouldn't count towards this percentage.
            # The request implies "non which is over 50% of users can see it",
            # which means if it's hidden, no one can see it, so it's 0%.
            if self.is_unlocked_for_user(user):
                unlocked_count += 1
        
        return (unlocked_count / len(eligible_users)) * 100 if eligible_users else 0.0

    @property
    def calculated_points(self):
        """
        Calculates the current points for the challenge, considering decay and unlock point reduction.
        """
        current_points = self.points
        now = datetime.now(UTC)

        # Apply existing point decay logic first
        if self.point_decay_type != 'STATIC' and self.point_decay_rate is not None:
            # Assuming 'submissions' relationship is ordered by timestamp for the first solve
            first_solve_time = None
            if self.proactive_decay:
                # Proactive decay starts from challenge creation or a set start time
                # For simplicity, let's assume it starts from now if no specific start time is set
                # or from the first submission if not proactive.
                # This part might need a dedicated 'decay_start_time' field in Challenge model
                # For now, let's assume proactive decay starts immediately.
                first_solve_time = now # Or a specific challenge creation time if available
            else:
                first_submission = Submission.query.filter_by(challenge_id=self.id).order_by(Submission.timestamp.asc()).first()
                if first_submission:
                    first_solve_time = first_submission.timestamp
                    # Ensure first_solve_time is UTC-aware if it's not already
                    if first_solve_time.tzinfo is None:
                        first_solve_time = first_solve_time.replace(tzinfo=UTC)

            if first_solve_time:
                time_since_first_solve = (now - first_solve_time).total_seconds() / 3600 # in hours

                if self.point_decay_type == 'LINEAR':
                    decay_amount = (self.point_decay_rate / 100) * time_since_first_solve
                    current_points = max(self.minimum_points, self.points - int(decay_amount))
                elif self.point_decay_type == 'LOGARITHMIC':
                    # Logarithmic decay: points = initial_points / (1 + rate * log(time))
                    # This is a simplified version, actual log decay might be more complex
                    if time_since_first_solve > 0:
                        decay_factor = 1 + (self.point_decay_rate / 100) * (time_since_first_solve ** 0.5) # Using sqrt for smoother log-like decay
                        current_points = max(self.minimum_points, int(self.points / decay_factor))
        
        # Apply unlock point reduction if applicable and challenge is considered "unlocked"
        # For point reduction purposes, we consider it unlocked if it has been solved at least once
        # or if it's generally unlocked by time/prerequisites for any user.
        # This logic needs to be carefully considered: should point reduction apply only after a user solves it,
        # or once it becomes generally available? The prompt implies "upon unlocking" which suggests general availability.
        # Let's assume point reduction applies if the challenge is generally available (i.e., unlock_date_time has passed
        # or prerequisites are met by *some* user, or if it's solved by *any* user).
        # For simplicity, let's assume point reduction applies if the challenge has been solved by at least one user.
        # A more robust solution might involve checking if the challenge is "globally" unlocked (e.g., timed unlock passed)
        # or if it's unlocked for the *current* user viewing it.
        # Given the prompt: "If a challenge has prerequisites and/or time-based unlocking, its points can dynamically adjust."
        # This implies the adjustment happens once the conditions are met, not necessarily tied to a specific user's solve.
        # Let's make a simplifying assumption: point reduction applies if the challenge's unlock_date_time has passed
        # OR if it has been solved by at least one user (implying it was unlocked for that user).
        
        # For the purpose of `calculated_points`, we need a global "unlocked" state, not user-specific.
        # The most straightforward global unlock condition is `unlock_date_time` if set.
        # If `unlock_date_time` is in the past, or if `unlock_type` is NONE, we consider it "globally" unlocked.
        # Prerequisite-based unlocks are user-specific, so they don't fit well into a global `calculated_points` property.
        # Let's refine: point reduction applies if the challenge is generally available (e.g., timed unlock passed)
        # OR if it has been solved by at least one user (meaning it was unlocked for them).
        
        # Let's simplify: point reduction applies if the challenge has been solved by at least one user.
        # This means we need to check if there are any submissions for this challenge.
        has_been_solved = Submission.query.filter_by(challenge_id=self.id).first() is not None
        
        # If unlock_date_time is set and in the past, it's also considered "unlocked" for point reduction purposes.
        is_timed_unlocked = self.unlock_date_time and now >= self.unlock_date_time

        if self.unlock_point_reduction_type != 'NONE' and (has_been_solved or is_timed_unlocked):
            if self.unlock_point_reduction_type == 'FIXED':
                current_points = max(self.minimum_points, current_points - (self.unlock_point_reduction_value or 0))
            elif self.unlock_point_reduction_type == 'PERCENTAGE':
                reduction_factor = (self.unlock_point_reduction_value or 0) / 100.0
                current_points = max(self.minimum_points, int(current_points * (1 - reduction_factor)))
            elif self.unlock_point_reduction_type == 'TIME_DECAY_TO_ZERO':
                if self.unlock_point_reduction_target_date and now < self.unlock_point_reduction_target_date:
                    time_to_target = (self.unlock_point_reduction_target_date - now).total_seconds()
                    total_decay_time = (self.unlock_point_reduction_target_date - (self.unlock_date_time or now)).total_seconds()
                    
                    if total_decay_time > 0:
                        decay_progress = 1 - (time_to_target / total_decay_time)
                        # Decay from initial points (before any other decay) down to minimum_points
                        # The initial points for this decay should be `self.points`
                        decayed_value = self.points - (self.points - self.minimum_points) * decay_progress
                        current_points = max(self.minimum_points, int(decayed_value))
                    else: # Target date is same as or before unlock date/now, so immediately minimum points
                        current_points = self.minimum_points
                elif self.unlock_point_reduction_target_date and now >= self.unlock_point_reduction_target_date:
                    current_points = self.minimum_points # Reached or passed target date, points are at minimum

        return current_points

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


