from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask import current_app # Import current_app

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'
bcrypt = Bcrypt()

def get_setting(key, default):
    from scripts.models import Setting # Import Setting model here to avoid circular dependency
    with current_app.app_context():
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            return setting.value
        return default
