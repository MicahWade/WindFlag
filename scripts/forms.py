from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from scripts.models import User, Category
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
    flag = StringField('Flag', validators=[DataRequired(), Length(min=1, max=100)])
    category = SelectField('Category', coerce=int, validators=[DataRequired()], choices=[(0, '--- Create New Category ---')])
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
        
        # If a new category name is provided, validate its uniqueness
        if self.new_category_name.data:
            existing_category = Category.query.filter_by(name=self.new_category_name.data).first()
            if existing_category:
                self.new_category_name.errors.append('A category with this name already exists.')
                return False
        return True
