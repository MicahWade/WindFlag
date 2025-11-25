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
    USERNAME_WORD_COUNT = int(os.environ.get('USERNAME_WORD_COUNT', 2))
    USERNAME_ADD_NUMBER = os.environ.get('USERNAME_ADD_NUMBER', 'True').lower() == 'true'
    PRESET_USER_COUNT = 50
    WORDS_FILE_PATH = os.environ.get('WORDS_FILE_PATH', 'words.text')
    ACTIVE_THEME = os.environ.get('ACTIVE_THEME', 'default')

    # New: Live Score Graph
    ENABLE_LIVE_SCORE_GRAPH = os.environ.get('ENABLE_LIVE_SCORE_GRAPH', 'True').lower() == 'true'

    # Rate Limiting Configuration
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '200 per day, 50 per hour')
    RATELIMIT_LOGIN = os.environ.get('RATELIMIT_LOGIN', '5 per minute')
    RATELIMIT_REGISTER = os.environ.get('RATELIMIT_REGISTER', '5 per hour')
    RATELIMIT_SUBMIT_FLAG = os.environ.get('RATELIMIT_SUBMIT_FLAG', '10 per minute')

    # GitHub SSO Configuration
    ENABLE_GITHUB_SSO = os.environ.get('ENABLE_GITHUB_SSO', 'False').lower() == 'true'
    GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')

    # Redis Cache Configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    ENABLE_REDIS_CACHE = os.environ.get('ENABLE_REDIS_CACHE', 'False').lower() == 'true'

class TestConfig(Config):
    """
    Configuration class for testing environments.
    Inherits from `Config` and overrides settings for testing purposes.
    """
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db' # Dedicated database for test mode
    WTF_CSRF_ENABLED = False
    DISABLE_SIGNUP = False # Allow signup in test mode for demo purposes



ACTIVE_THEME = '8bit'
