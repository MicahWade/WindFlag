import os
from scripts.extensions import db
from scripts.models import Setting

THEMES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'themes')

def scan_themes():
    """
    Scans the themes directory for valid themes.
    A valid theme is a subdirectory containing a theme.css file.
    Returns a list of theme names.
    """
    themes = []
    if not os.path.exists(THEMES_DIR):
        return themes

    for item in os.listdir(THEMES_DIR):
        theme_path = os.path.join(THEMES_DIR, item)
        if os.path.isdir(theme_path):
            css_file_path = os.path.join(theme_path, 'theme.css')
            if os.path.exists(css_file_path):
                themes.append(item)
    return sorted(themes)

def get_active_theme():
    """
    Retrieves the currently active theme from the database.
    Assumes an application context is already active.
    """
    from flask import current_app
    setting = Setting.query.filter_by(key='ACTIVE_THEME').first()
    if setting:
        return setting.value
    return 'default' # Default theme if not found in DB

def set_active_theme(theme_name):
    """
    Sets the active theme in the database.
    """
    # Use Flask's application context to access the database
    from flask import current_app
    with current_app.app_context():
        setting = Setting.query.filter_by(key='ACTIVE_THEME').first()
        if setting:
            setting.value = theme_name
        else:
            setting = Setting(key='ACTIVE_THEME', value=theme_name)
            db.session.add(setting)
        db.session.commit()

