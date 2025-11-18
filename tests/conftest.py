import pytest
from app import create_app
from scripts.extensions import db, bcrypt
from scripts.models import User, Category, Challenge, Submission, Setting, ChallengeFlag, FlagSubmission, MULTI_FLAG_TYPES
from datetime import datetime, UTC, timedelta
import os
from scripts.config import TestConfig # Import TestConfig
import uuid # Import uuid

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
        # Create a test user with a unique email and username
        unique_id = uuid.uuid4()
        hashed_password = bcrypt.generate_password_hash("password").decode('utf-8')
        user = User(username=f"testuser_{unique_id}", email=f"testuser_{unique_id}@example.com", password_hash=hashed_password) # Use UUID for unique username and email
        db.session.add(user)
        db.session.commit()

        # Create a test category with a unique name
        category = Category(name=f"Test Category {uuid.uuid4()}") # Use UUID for unique category name
        db.session.add(category)
        db.session.commit()

        # Create a test challenge (SINGLE type for backward compatibility)
        challenge = Challenge(name="Test Challenge", description="This is a test challenge.",
                              points=100, case_sensitive=True, category_id=category.id,
                              multi_flag_type='SINGLE') # Set to SINGLE
        db.session.add(challenge)
        db.session.commit()
        # Add a single flag for this challenge
        challenge_flag = ChallengeFlag(challenge_id=challenge.id, flag_content="TESTFLAG")
        db.session.add(challenge_flag)
        db.session.commit()


        # Get a test client
        with app.test_client() as client:
            # Manually log in the user for the test client session
            with client.session_transaction() as session:
                session['_user_id'] = str(user.id)
                session['_fresh'] = True # Mark session as fresh if needed by Flask-Login

            yield client, user, challenge # Yield client, user, and challenge

@pytest.fixture(scope='function')
def multi_flag_challenge_setup(app):
    with app.app_context():
        # Create a test user with a unique email and username
        unique_id = uuid.uuid4()
        hashed_password = bcrypt.generate_password_hash("multiflagpass").decode('utf-8')
        user = User(username=f"multiflaguser_{unique_id}", email=f"multiflaguser_{unique_id}@example.com", password_hash=hashed_password) # Use UUID for unique username and email
        db.session.add(user)
        db.session.commit()

        # Create a test category with a unique name
        category = Category(name=f"MultiFlag Category {uuid.uuid4()}") # Use UUID for unique category name
        db.session.add(category)
        db.session.commit()

        # Create a client and log in the user
        client = app.test_client()
        with client.session_transaction() as session:
            session['_user_id'] = str(user.id)
            session['_fresh'] = True

        yield client, user, category

from scripts.seed import seed_database

@pytest.fixture(scope='function') # Changed scope to function to ensure fresh data for each test
def seed_data(app):
    with app.app_context():
        # seed_database now returns IDs
        seeded_ids = seed_database()
        yield seeded_ids
