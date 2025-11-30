from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, SelectField, SelectMultipleField, HiddenField
from wtforms.fields.datetime import DateTimeField, DateField # Import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from scripts.models import User, Category, MULTI_FLAG_TYPES, POINT_DECAY_TYPES, UNLOCK_TYPES, DYNAMIC_FLAG_TYPE, CHALLENGE_TYPES # Import DYNAMIC_FLAG_TYPE and CHALLENGE_TYPES
from flask import current_app
import json
import pytz # Re-add pytz import

def _get_timezone_choices():
    """
    Returns a list of common timezone choices for a SelectField.
    """
    return [(tz, tz) for tz in pytz.common_timezones]

class RegistrationForm(FlaskForm):
    """
    Form for user registration. Dynamically sets validators for email and join code
    based on application configuration.
    """
    # username field is handled dynamically in __init__
    email = StringField('Email') # Define email field, validators set dynamically
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    join_code = StringField('Join Code') # Define join_code field, validators set dynamically
    submit = SubmitField('Sign Up')

    def __init__(self, config, *args, **kwargs):
        """
        Initializes the RegistrationForm and dynamically sets validators
        for email and join_code based on the provided application configuration.
        It also conditionally includes the username field.

        Args:
            config (dict): The application configuration dictionary.
        """
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.config = config

        # Conditionally add username field and its validation
        if not self.config.get('PRESET_USERNAMES_ENABLED', False):
            self.username = StringField('Username',
                                        validators=[DataRequired(), Length(min=2, max=20)])
            # Dynamically add the validate_username method if the field is present
            setattr(self, 'validate_username', self._validate_dynamic_username)
        else:
            # If PRESET_USERNAMES_ENABLED is true, remove the username field if it exists
            if hasattr(self, 'username'):
                delattr(self, 'username')

        # Dynamically set validators for the email field based on app configuration
        email_validators = []
        if self.config['REQUIRE_EMAIL']:
            email_validators.append(DataRequired())
            email_validators.append(Email())
        self.email.validators = email_validators

        # Dynamically set validators for the join_code field based on app configuration
        join_code_validators = []
        if self.config['REQUIRE_JOIN_CODE']:
            join_code_validators.append(DataRequired())
        self.join_code.validators = join_code_validators
    
    def _validate_dynamic_username(self, field):
        """
        Validates that the chosen username is not already taken.
        This method is dynamically added if PRESET_USERNAMES_ENABLED is False.
        """
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        """
        Validates that the chosen email is not already taken, if email is required by config.

        Args:
            email (StringField): The email field from the form.

        Raises:
            ValidationError: If the email already exists and is required.
        """
        # Only perform email validation if email is required by the configuration
        if self.config['REQUIRE_EMAIL']:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    """
    Form for user login.
    """
    username = StringField('Username',
                           validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class FlagSubmissionForm(FlaskForm):
    """
    Form for submitting a flag to solve a challenge.
    """
    flag = StringField('Flag', validators=[DataRequired()])
    submit = SubmitField('Submit Flag')

class CategoryForm(FlaskForm):
    """
    Form for creating and updating challenge categories.
    """
    name = StringField('Category Name',
                       validators=[DataRequired(), Length(min=2, max=50)])
    
    # New fields for category unlocking (similar to ChallengeForm)
    unlock_type = SelectField('Unlock Type',
                              choices=[(t, t.replace('_', ' ').title()) for t in UNLOCK_TYPES],
                              validators=[DataRequired()],
                              default='NONE')
    prerequisite_percentage_value = IntegerField('Prerequisite Percentage Value',
                                                 validators=[NumberRange(min=0, max=100)],
                                                 render_kw={"placeholder": "e.g., 50 for 50% of challenges"})
    prerequisite_count_value = IntegerField('Prerequisite Count Value',
                                            validators=[NumberRange(min=0)],
                                            render_kw={"placeholder": "e.g., 5 for 5 challenges"})
    prerequisite_count_category_ids_input = HiddenField('Prerequisite Count Categories') # Populated by JS
    prerequisite_challenge_ids_input = HiddenField('Prerequisite Challenge IDs') # Populated by JS
    timezone = SelectField('Timezone', choices=[], default='Australia/Sydney') # New timezone field
    unlock_date_time = DateField('Unlock Date', format='%Y-%m-%d',
                                     render_kw={"placeholder": "YYYY-MM-DD"})
    is_hidden = BooleanField('Hide Category from Users', default=False) # New: Field to hide category

    submit = SubmitField('Submit Category')

    def validate_name(self, name):
        """
        Validates that the chosen category name is not already taken.

        Args:
            name (StringField): The name field from the form.

        Raises:
            ValidationError: If the category name already exists.
        """
        # Import here to avoid circular dependency
        from scripts.models import Category
        category = Category.query.filter_by(name=name.data).first()
        if category and category.id != self.category_id.data: # Allow updating existing category with same name
            raise ValidationError('That category name is taken. Please choose a different one.')
    
    # Add a HiddenField for category_id to allow validation during updates
    category_id = HiddenField()

    def validate(self, extra_validators=None):
        """
        Performs custom validation for the CategoryForm, including unlock fields.
        """
        if not super().validate(extra_validators=extra_validators):
            return False
        
        # Validate unlock fields (similar to ChallengeForm)
        if self.unlock_type.data in ['PREREQUISITE_PERCENTAGE', 'COMBINED']:
            if self.prerequisite_percentage_value.data is None or self.prerequisite_percentage_value.data < 0:
                self.prerequisite_percentage_value.errors.append('Prerequisite percentage value is required for this unlock type.')
                return False
        
        if self.unlock_type.data in ['PREREQUISITE_COUNT', 'COMBINED']:
            if self.prerequisite_count_value.data is None or self.prerequisite_count_value.data < 0:
                self.prerequisite_count_value.errors.append('Prerequisite count value is required for this unlock type.')
                return False
            
            try:
                prerequisite_category_ids = json.loads(self.prerequisite_count_category_ids_input.data or '[]')
                if prerequisite_category_ids and not self.prerequisite_count_value.data:
                    self.prerequisite_count_value.errors.append('Prerequisite count value must be set if categories are selected for count.')
                    return False
            except json.JSONDecodeError:
                self.prerequisite_count_category_ids_input.errors.append('Invalid format for prerequisite count category IDs.')
                return False

        if self.unlock_type.data in ['TIMED', 'COMBINED']:
            if not self.unlock_date_time.data:
                self.unlock_date_time.errors.append('Unlock date is required for this unlock type.')
                return False
        
        return True

class ChallengeForm(FlaskForm):
    """
    Form for creating and updating challenges. Includes fields for multi-flag challenges
    and dynamic category selection, as well as challenge unlocking and point adjustment.
    """
    name = StringField('Challenge Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    points = IntegerField('Points', validators=[DataRequired(), NumberRange(min=1)])
    minimum_points = IntegerField('Minimum Points', validators=[DataRequired(), NumberRange(min=1)], default=1)
    point_decay_type = SelectField('Point Decay Type',
                                   choices=[(t, t.replace('_', ' ').title()) for t in POINT_DECAY_TYPES],
                                   validators=[DataRequired()],
                                   default='STATIC')
    point_decay_rate = IntegerField('Point Decay Rate',
                                    validators=[NumberRange(min=0)],
                                    default=0)
    proactive_decay = BooleanField('Apply decay proactively', default=False)
    
    # Challenge Type Selection
    challenge_type = SelectField('Challenge Type',
                                choices=[(t, t.title()) for t in CHALLENGE_TYPES],
                                validators=[DataRequired()],
                                default='FLAG')

    # Fields for FLAG challenges
    multi_flag_type = SelectField('Flag Type',
                                  choices=[(t, t.replace('_', ' ').title()) for t in MULTI_FLAG_TYPES],
                                  validators=[DataRequired()],
                                  default='SINGLE')
    multi_flag_threshold = IntegerField('N of M Threshold (for N_OF_M type)',
                                        validators=[NumberRange(min=1)],
                                        render_kw={"placeholder": "Required for N_OF_M type"},
                                        default=1) # Default to 1, but will be validated based on type
    
    flags_input = TextAreaField('Flags (one per line)',
                                validators=[], # Removed DataRequired here, will validate conditionally
                                render_kw={"rows": 5, "placeholder": "Enter each flag on a new line"})

    case_sensitive = BooleanField('Flags are Case-Sensitive', default=True)

    # Fields for CODING challenges
    language = SelectField('Language',
                           choices=[('python3', 'Python 3'),
                                    ('nodejs', 'Node.js'),
                                    ('php', 'PHP'),
                                    ('bash', 'Bash'),
                                    ('dart', 'Dart')],
                           default='python3')
    expected_output = TextAreaField('Expected Output',
                                    render_kw={"rows": 5, "placeholder": "Exact expected STDOUT from the executed code"})
    test_case_input = TextAreaField('Test Case Input (Optional)',
                                    render_kw={"rows": 3, "placeholder": "Input provided to STDIN of the executed code"})
    setup_code = TextAreaField('Setup Code (Optional)',
                               render_kw={"rows": 5, "placeholder": "Code/Script to run before the user's code (e.g., database setup)"})
    starter_code = TextAreaField('Starter Code (Optional)',
                                 render_kw={"rows": 5, "placeholder": "Default code provided to the user"})


    category = SelectField('Category', coerce=int, choices=[(0, '--- Create New Category ---')])
    new_category_name = StringField('New Category Name', validators=[Length(max=50)])

    # New fields for challenge unlocking
    unlock_type = SelectField('Unlock Type',
                              choices=[(t, t.replace('_', ' ').title()) for t in UNLOCK_TYPES],
                              validators=[DataRequired()],
                              default='NONE')
    prerequisite_percentage_value = IntegerField('Prerequisite Percentage Value',
                                                 validators=[NumberRange(min=0, max=100)],
                                                 render_kw={"placeholder": "e.g., 50 for 50% of challenges"})
    prerequisite_count_value = IntegerField('Prerequisite Count Value',
                                            validators=[NumberRange(min=0)],
                                            render_kw={"placeholder": "e.g., 5 for 5 challenges"})
    prerequisite_count_category_ids_input = HiddenField('Prerequisite Count Categories') # Changed to HiddenField
    prerequisite_challenge_ids_input = HiddenField('Prerequisite Challenge IDs') # Changed to HiddenField
    timezone = SelectField('Timezone', choices=[], default='Australia/Sydney') # New timezone field
    unlock_date_time = DateField('Unlock Date', format='%Y-%m-%d',
                                     render_kw={"placeholder": "YYYY-MM-DD"})
    unlock_point_reduction_type = SelectField('Unlock Point Reduction Type',
                                               choices=[('NONE', 'None'), ('PERCENTAGE', 'Percentage'), ('FIXED', 'Fixed')],
                                               default='NONE')
    unlock_point_reduction_value = IntegerField('Unlock Point Reduction Value',
                                                validators=[NumberRange(min=0)],
                                                default=0)
    unlock_point_reduction_target_date = DateField('Unlock Point Reduction Target Date', format='%Y-%m-%d',
                                                     render_kw={"placeholder": "YYYY-MM-DD"})

    is_hidden = BooleanField('Hide Challenge from Users', default=False) # New: Field to hide challenge
    has_dynamic_flag = BooleanField('Has Dynamic Flag', default=False) # New: Field to enable/disable dynamic flag
    submit = SubmitField('Submit Challenge')

    def validate(self, extra_validators=None):
        """
        Performs custom validation for the ChallengeForm, including category selection,
        multi-flag type, threshold, flag count, and new unlock fields.

        Args:
            extra_validators: Optional extra validators to run.

        Returns:
            bool: True if validation passes, False otherwise.
        """
        if not super().validate(extra_validators=extra_validators):
            return False
        
        # Ensure either an existing category is selected (not the default 0) OR a new category name is provided, but not both.
        if self.category.data == 0 and not self.new_category_name.data:
            self.category.errors.append('Please select an existing category or provide a new category name.')
            return False
        if self.category.data != 0 and self.new_category_name.data:
            self.new_category_name.errors.append('Cannot select an existing category and provide a new category name.')
            return False
        
        # Validate based on challenge_type
        if self.challenge_type.data == 'CODING':
            if not self.language.data:
                self.language.errors.append('Language is required for Coding challenges.')
                return False
            if not self.expected_output.data:
                self.expected_output.errors.append('Expected Output is required for Coding challenges.')
                return False
        else: # FLAG type
            # Validate multi_flag_type and threshold
            if self.multi_flag_type.data == DYNAMIC_FLAG_TYPE:
                # For dynamic flags, traditional flags_input and threshold are not required
                pass # No specific flag input validation for dynamic type
            elif self.multi_flag_type.data == 'N_OF_M':
                if not self.multi_flag_threshold.data or self.multi_flag_threshold.data < 1:
                    self.multi_flag_threshold.errors.append('Threshold is required and must be at least 1 for N_OF_M type.')
                    return False
                
                # Count the number of flags provided
                provided_flags = [f.strip() for f in self.flags_input.data.split('\n') if f.strip()]
                if self.multi_flag_threshold.data > len(provided_flags):
                    self.multi_flag_threshold.errors.append(f'Threshold ({self.multi_flag_threshold.data}) cannot be greater than the number of provided flags ({len(provided_flags)}).')
                    return False
                if not provided_flags:
                    self.flags_input.errors.append('At least one flag is required for N_OF_M type.')
                    return False
            elif self.multi_flag_type.data == 'SINGLE':
                provided_flags = [f.strip() for f in self.flags_input.data.split('\n') if f.strip()]
                if len(provided_flags) != 1:
                    self.flags_input.errors.append('SINGLE type challenges must have exactly one flag.')
                    return False
                if not provided_flags:
                    self.flags_input.errors.append('At least one flag is required for SINGLE type.')
                    return False
            else: # 'ANY', 'ALL'
                provided_flags = [f.strip() for f in self.flags_input.data.split('\n') if f.strip()]
                if not provided_flags:
                    self.flags_input.errors.append('At least one flag is required for this multi-flag type.')
                    return False
        
        # Validate unlock fields
        if self.unlock_type.data in ['PREREQUISITE_PERCENTAGE', 'COMBINED']:
            if self.prerequisite_percentage_value.data is None or self.prerequisite_percentage_value.data < 0:
                self.prerequisite_percentage_value.errors.append('Prerequisite percentage value is required for this unlock type.')
                return False
        
        if self.unlock_type.data in ['PREREQUISITE_COUNT', 'COMBINED']:
            if self.prerequisite_count_value.data is None or self.prerequisite_count_value.data < 0:
                self.prerequisite_count_value.errors.append('Prerequisite count value is required for this unlock type.')
                return False
            
            try:
                # The data from the hidden field will be a JSON string
                prerequisite_category_ids = json.loads(self.prerequisite_count_category_ids_input.data or '[]')
                # If prerequisite_count_value is set, and categories are selected, ensure categories are valid.
                # If no categories are selected, it implies count applies to all challenges.
                if prerequisite_category_ids and not self.prerequisite_count_value.data:
                    self.prerequisite_count_value.errors.append('Prerequisite count value must be set if categories are selected for count.')
                    return False
            except json.JSONDecodeError:
                self.prerequisite_count_category_ids_input.errors.append('Invalid format for prerequisite count category IDs.')
                return False

        if self.unlock_type.data in ['TIMED', 'COMBINED']:
            if not self.unlock_date_time.data:
                self.unlock_date_time.errors.append('Unlock date and time is required for this unlock type.')
                return False
        
        return True


class AdminSettingsForm(FlaskForm):
    """
    Form for configuring various administrative settings of the platform,
    including scoreboard display and profile chart toggles.
    """
    top_x_scoreboard = IntegerField('Top X Scoreboard',
                                    validators=[DataRequired(), NumberRange(min=1, max=100)],
                                    default=10)
    scoreboard_graph_type = SelectField('Scoreboard Graph Type',
                                        choices=[('line', 'Line Graph'), ('area', 'Area Graph')],
                                        validators=[DataRequired()],
                                        default='line')
    profile_points_over_time_chart_enabled = BooleanField('Enable "Points Over Time" Chart on Profile', default=True)
    profile_fails_vs_succeeds_chart_enabled = BooleanField('Enable "Fails vs. Succeeds" Chart on Profile', default=True)
    profile_categories_per_score_chart_enabled = BooleanField('Enable "Categories per Score" Chart on Profile', default=True)
    profile_challenges_complete_chart_enabled = BooleanField('Enable "Challenges Complete" Chart on Profile', default=True)
    timezone = SelectField('Default Timezone', choices=_get_timezone_choices(), validators=[DataRequired()], default='Australia/Sydney') # New: Timezone setting
    accordion_display_style = SelectField('Accordion Display Style',
                                        choices=[('boxes', 'Boxes'), ('lines', 'Lines')],
                                        validators=[DataRequired()],
                                        default='boxes')
    enable_live_score_graph = BooleanField('Enable Live Scoreboard Graph', default=True)

    submit = SubmitField('Save Settings')

class AwardCategoryForm(FlaskForm):
    """
    Form for creating and updating award categories.
    """
    name = StringField('Category Name',
                       validators=[DataRequired(), Length(min=2, max=50)])
    default_points = IntegerField('Default Points',
                                  validators=[DataRequired(), NumberRange(min=0)],
                                  default=0)
    submit = SubmitField('Submit Category')

    def validate_name(self, name):
        """
        Validates that the chosen award category name is not already taken.

        Args:
            name (StringField): The name field from the form.

        Raises:
            ValidationError: If the award category name already exists.
        """
        from scripts.models import AwardCategory # Import here to avoid circular dependency
        category = AwardCategory.query.filter_by(name=name.data).first()
        if category:
            raise ValidationError('That award category name is taken. Please choose a different one.')

class InlineGiveAwardForm(FlaskForm):
    """
    Form for giving an award to a user directly from their profile page.
    """
    category = SelectField('Award Category', coerce=int, validators=[DataRequired()])
    points = IntegerField('Points to Award',
                          validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Give Award')

class PasswordResetForm(FlaskForm):
    """
    Form for users to reset their password.
    """
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)]) # Enforce minimum 8 chars for new password
    confirm_password = PasswordField('Confirm New Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
