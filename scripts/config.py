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
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db' # Changed to app.db for main database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REQUIRE_JOIN_CODE = os.environ.get('REQUIRE_JOIN_CODE', 'False').lower() == 'true'
    JOIN_CODE = os.environ.get('JOIN_CODE') if REQUIRE_JOIN_CODE else None
    REQUIRE_EMAIL = os.environ.get('REQUIRE_EMAIL', 'True').lower() == 'true'
    BASIC_INDEX_PAGE = os.environ.get('BASIC_INDEX_PAGE', 'False').lower() == 'true'
    DISABLE_SIGNUP = os.environ.get('DISABLE_SIGNUP', 'False').lower() == 'true'
    TIMEZONE = os.environ.get('TIMEZONE', 'UTC') # New: Timezone setting

class TestConfig(Config):
    """
    Configuration class for testing environments.
    Inherits from `Config` and overrides settings for testing purposes.
    """
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db' # Dedicated database for test mode
    WTF_CSRF_ENABLED = False
    DISABLE_SIGNUP = False # Allow signup in test mode for demo purposes
