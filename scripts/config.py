import os
# from dotenv import load_dotenv # Removed as it's now handled in app.py

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# load_dotenv(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), '.env')) # Removed

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db' # Changed to app.db for main database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REQUIRE_JOIN_CODE = os.environ.get('REQUIRE_JOIN_CODE', 'False').lower() == 'true'
    JOIN_CODE = os.environ.get('JOIN_CODE') if REQUIRE_JOIN_CODE else None
    REQUIRE_EMAIL = os.environ.get('REQUIRE_EMAIL', 'True').lower() == 'true'

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_mode.db' # Dedicated database for test mode
    WTF_CSRF_ENABLED = False
