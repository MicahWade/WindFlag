"""
This module initializes Flask extensions used in the WindFlag CTF platform.
It also provides a utility function for retrieving application settings from the database.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask import current_app

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'
bcrypt = Bcrypt()

def get_setting(key, default):
    """
    Retrieves a setting value from the database.

    Args:
        key (str): The key of the setting to retrieve.
        default: The default value to return if the setting is not found.

    Returns:
        str: The value of the setting, or the default value if not found.
    """
    from scripts.models import Setting # Import Setting model here to avoid circular dependency
    with current_app.app_context():
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            return setting.value
        return default
