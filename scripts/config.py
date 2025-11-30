"""
This module defines the configuration classes for the WindFlag CTF platform.
It includes settings for the Flask application, database, and various features.
"""
import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    """
    Base configuration class for the Flask application.
    Loads settings from environment variables or uses default values.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    USE_POSTGRES = os.environ.get('USE_POSTGRES', 'False').lower() == 'true'

    if USE_POSTGRES:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db' # Default to SQLite if PostgreSQL not used

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REQUIRE_JOIN_CODE = os.environ.get('REQUIRE_JOIN_CODE', 'False').lower() == 'true'
    JOIN_CODE = os.environ.get('JOIN_CODE') if REQUIRE_JOIN_CODE else None
    REQUIRE_EMAIL = os.environ.get('REQUIRE_EMAIL', 'True').lower() == 'true'
    BASIC_INDEX_PAGE = os.environ.get('BASIC_INDEX_PAGE', 'False').lower() == 'true'
    DISABLE_SIGNUP = os.environ.get('DISABLE_SIGNUP', 'False').lower() == 'true'
    TIMEZONE = os.environ.get('TIMEZONE', 'UTC') # New: Timezone setting
    USERNAME_WORD_COUNT = int(os.environ.get('USERNAME_WORD_COUNT', 2))
    USERNAME_ADD_NUMBER = os.environ.get('USERNAME_ADD_NUMBER', 'True').lower() == 'true'
    PRESET_USER_COUNT = 50
    WORDS_FILE_PATH = os.environ.get('WORDS_FILE_PATH', 'words.text')
    ACTIVE_THEME = os.environ.get('ACTIVE_THEME', 'default')

    # Admin API Key
    ADMIN_API_KEY = os.environ.get('ADMIN_API_KEY')

    # Language Execution Enable/Disable Flags
    ENABLE_PYTHON3 = os.environ.get('ENABLE_PYTHON3', 'True').lower() == 'true'
    ENABLE_NODEJS = os.environ.get('ENABLE_NODEJS', 'True').lower() == 'true'
    ENABLE_PHP = os.environ.get('ENABLE_PHP', 'True').lower() == 'true'
    ENABLE_BASH = os.environ.get('ENABLE_BASH', 'True').lower() == 'true'
    ENABLE_DART = os.environ.get('ENABLE_DART', 'True').lower() == 'true'

    # Rate Limiting Configuration
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '200 per day, 50 per hour')
    RATELIMIT_LOGIN = os.environ.get('RATELIMIT_LOGIN', '5 per minute')
    RATELIMIT_REGISTER = os.environ.get('RATELIMIT_REGISTER', '5 per hour')
    RATELIMIT_SUBMIT_FLAG = os.environ.get('RATELIMIT_SUBMIT_FLAG', '10 per minute')

    UPLOAD_FOLDER = os.path.join(basedir, 'instance', 'uploads')

def get_enabled_language_configs():
    """
    Returns a dictionary of enabled languages and their configurations
    based on the current Flask application's configuration.
    """
    from flask import current_app
    enabled_languages = {}
    
    # Define all possible languages that can be enabled/disabled
    # This list should match the ENABLE_X flags in Config class
    all_possible_languages = ['python3', 'nodejs', 'php', 'bash', 'dart']

    for lang in all_possible_languages:
        enable_flag = f'ENABLE_{lang.upper()}'
        if current_app.config.get(enable_flag, False): # Default to False if flag not found
            enabled_languages[lang] = True # Store some placeholder or actual config if needed
            
    return enabled_languages

class TestConfig(Config):
    """
    Configuration class for testing environments.
    Inherits from `Config` and overrides settings for testing purposes.
    """
    if os.environ.get('USE_POSTGRES', 'False').lower() == 'true':
        SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'postgresql://localhost/test_db'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db' # Dedicated database for test mode
    WTF_CSRF_ENABLED = False
    DISABLE_SIGNUP = False # Allow signup in test mode for demo purposes




ACTIVE_THEME = '8bit'
