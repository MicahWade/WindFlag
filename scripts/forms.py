from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from scripts.models import User, Category, MULTI_FLAG_TYPES # Import MULTI_FLAG_TYPES
from flask import current_app # Import current_app

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email') # Define email field, validators set dynamically
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    join_code = StringField('Join Code') # Define join_code field, validators set dynamically
    submit = SubmitField('Sign Up')

    def __init__(self, config, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.config = config

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

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        # Only perform email validation if email is required by the configuration
        if self.config['REQUIRE_EMAIL']:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class FlagSubmissionForm(FlaskForm):
    flag = StringField('Flag', validators=[DataRequired()])
    submit = SubmitField('Submit Flag')

class CategoryForm(FlaskForm):
    name = StringField('Category Name',
                       validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Submit Category')

    def validate_name(self, name):
        category = Category.query.filter_by(name=name.data).first()
        if category:
            raise ValidationError('That category name is taken. Please choose a different one.')

class ChallengeForm(FlaskForm):
    name = StringField('Challenge Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    points = IntegerField('Points', validators=[DataRequired(), NumberRange(min=1)])
    
    # Removed 'flag' field
    # New fields for multi-flag challenges
    multi_flag_type = SelectField('Multi-Flag Type',
                                  choices=[(t, t.replace('_', ' ').title()) for t in MULTI_FLAG_TYPES],
                                  validators=[DataRequired()],
                                  default='SINGLE')
    multi_flag_threshold = IntegerField('N of M Threshold (for N_OF_M type)',
                                        validators=[NumberRange(min=1)],
                                        render_kw={"placeholder": "Required for N_OF_M type"},
                                        default=1) # Default to 1, but will be validated based on type
    
    flags_input = TextAreaField('Flags (one per line)',
                                validators=[DataRequired()],
                                render_kw={"rows": 5, "placeholder": "Enter each flag on a new line"})

    case_sensitive = BooleanField('Flags are Case-Sensitive', default=True)
    category = SelectField('Category', coerce=int, choices=[(0, '--- Create New Category ---')])
    new_category_name = StringField('New Category Name', validators=[Length(max=50)])
    submit = SubmitField('Submit Challenge')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False
        
        # Ensure either an existing category is selected (not the default 0) OR a new category name is provided, but not both.
        if self.category.data == 0 and not self.new_category_name.data:
            self.category.errors.append('Please select an existing category or provide a new category name.')
            return False
        if self.category.data != 0 and self.new_category_name.data:
            self.new_category_name.errors.append('Cannot select an existing category and provide a new category name.')
            return False
        
        # Validate multi_flag_type and threshold
        if self.multi_flag_type.data == 'N_OF_M':
            if not self.multi_flag_threshold.data or self.multi_flag_threshold.data < 1:
                self.multi_flag_threshold.errors.append('Threshold is required and must be at least 1 for N_OF_M type.')
                return False
            
            # Count the number of flags provided
            provided_flags = [f.strip() for f in self.flags_input.data.split('\n') if f.strip()]
            if self.multi_flag_threshold.data > len(provided_flags):
                self.multi_flag_threshold.errors.append(f'Threshold ({self.multi_flag_threshold.data}) cannot be greater than the number of provided flags ({len(provided_flags)}).')
                return False
        elif self.multi_flag_type.data == 'SINGLE':
            provided_flags = [f.strip() for f in self.flags_input.data.split('\n') if f.strip()]
            if len(provided_flags) != 1:
                self.flags_input.errors.append('SINGLE type challenges must have exactly one flag.')
                return False
        
        return True

class AdminSettingsForm(FlaskForm):
    top_x_scoreboard = IntegerField('Top X Scoreboard',
                                    validators=[DataRequired(), NumberRange(min=1, max=100)],
                                    default=10)
    scoreboard_graph_type = SelectField('Scoreboard Graph Type',
                                        choices=[('line', 'Line Graph'), ('area', 'Area Graph')],
                                        validators=[DataRequired()],
                                        default='line')
    
    # New fields for profile chart toggles
    profile_points_over_time_chart_enabled = BooleanField('Enable "Points Over Time" Chart on Profile', default=True)
    profile_fails_vs_succeeds_chart_enabled = BooleanField('Enable "Fails vs. Succeeds" Chart on Profile', default=True)
    profile_categories_per_score_chart_enabled = BooleanField('Enable "Categories per Score" Chart on Profile', default=True)
    profile_challenges_complete_chart_enabled = BooleanField('Enable "Challenges Complete" Chart on Profile', default=True)

    submit = SubmitField('Save Settings')

class AwardCategoryForm(FlaskForm):
    name = StringField('Category Name',
                       validators=[DataRequired(), Length(min=2, max=50)])
    default_points = IntegerField('Default Points',
                                  validators=[DataRequired(), NumberRange(min=0)],
                                  default=0)
    submit = SubmitField('Submit Category')

    def validate_name(self, name):
        from scripts.models import AwardCategory # Import here to avoid circular dependency
        category = AwardCategory.query.filter_by(name=name.data).first()
        if category:
            raise ValidationError('That award category name is taken. Please choose a different one.')

class InlineGiveAwardForm(FlaskForm):
    category = SelectField('Award Category', coerce=int, validators=[DataRequired()])
    points = IntegerField('Points to Award',
                          validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Give Award')


