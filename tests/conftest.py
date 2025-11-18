import pytest
from app import create_app
from scripts.extensions import db, bcrypt
from scripts.models import User, Category, Challenge, Submission, Setting
from datetime import datetime, UTC, timedelta
import os
from scripts.config import TestConfig # Import TestConfig

@pytest.fixture(scope='session')
def app():
    # Use a separate test database
    app = create_app(config_class=TestConfig)
    with app.app_context():
        # Ensure the test database file is removed before creating tables
        test_db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        db.create_all()
        yield app
        db.drop_all()
        # Optionally remove the database file after tests as well
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def auth_client(app):
    with app.app_context():
        # Create a test user
        hashed_password = bcrypt.generate_password_hash("password").decode('utf-8')
        user = User(username="testuser", email="test@example.com", password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()

        # Create a test category
        category = Category(name="Test Category")
        db.session.add(category)
        db.session.commit()

        # Create a test challenge
        challenge = Challenge(name="Test Challenge", description="This is a test challenge.",
                              points=100, flag="TESTFLAG", case_sensitive=True, category_id=category.id)
        db.session.add(challenge)
        db.session.commit()

        # Get a test client
        with app.test_client() as client:
            # Manually log in the user for the test client session
            with client.session_transaction() as session:
                session['_user_id'] = str(user.id)
                session['_fresh'] = True # Mark session as fresh if needed by Flask-Login

            yield client, user, challenge # Yield client, user, and challenge

from scripts.seed import seed_database

@pytest.fixture(scope='session')
def seed_data(app):
    with app.app_context():
        # seed_database now returns IDs
        seeded_ids = seed_database()
        yield seeded_ids