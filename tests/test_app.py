import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app import create_app
from scripts.config import TestConfig # Import TestConfig
from scripts.extensions import db, bcrypt # Import db and bcrypt
from scripts.models import User, Category, Challenge # Import models

@pytest.fixture
def app():
    app = create_app(config_class=TestConfig) # Use TestConfig
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_flag_submission_case_insensitive_challenge(app, auth_client):
    client, user, _ = auth_client # We don't need the default challenge from auth_client

    with app.app_context():
        # Create a test category if it doesn't exist
        category = Category.query.filter_by(name="Insensitive Category").first()
        if not category:
            category = Category(name="Insensitive Category")
            db.session.add(category)
            db.session.commit()
        category_id = category.id

        # Create a case-insensitive challenge
        case_insensitive_challenge = Challenge(name="Case Insensitive Challenge", description="This is a case insensitive challenge.",
                                               points=100, flag="INSENSITIVEFLAG", case_sensitive=False, category_id=category_id)
        db.session.add(case_insensitive_challenge)
        db.session.commit()
        case_insensitive_challenge_id = case_insensitive_challenge.id
        case_insensitive_challenge_points = case_insensitive_challenge.points

    # Test with lowercase flag
    response = client.post(f'/submit_flag/{case_insensitive_challenge_id}', data={'flag': 'insensitiveflag'})
    assert response.status_code == 200
    assert response.json['success'] == True
    assert response.json['message'] == f'Correct Flag! You earned {case_insensitive_challenge_points} points!'

    # Test with mixed case flag (should also succeed)
    response = client.post(f'/submit_flag/{case_insensitive_challenge_id}', data={'flag': 'InSeNsItIvEfLaG'})
    assert response.status_code == 200
    assert response.json['success'] == False # Should be false because already solved
    assert response.json['message'] == 'You have already solved this challenge!'

def test_flag_submission_case_sensitive_challenge(app): # Removed auth_client fixture
    with app.app_context():
        # Create a unique test user for this test
        hashed_password = bcrypt.generate_password_hash("cs_password").decode('utf-8')
        cs_user = User(username="cs_testuser", email="cs_test@example.com", password_hash=hashed_password)
        db.session.add(cs_user)
        db.session.commit()
        cs_user_id = cs_user.id # Get ID here

        # Create a test category if it doesn't exist
        cs_category = Category.query.filter_by(name="CS Category").first()
        if not cs_category:
            cs_category = Category(name="CS Category")
            db.session.add(cs_category)
            db.session.commit()
        cs_category_id = cs_category.id # Get ID here

        # Create a case-sensitive challenge
        case_sensitive_challenge = Challenge(name="Case Sensitive Challenge", description="This is a case sensitive challenge.",
                                             points=150, flag="CASEFLAG", case_sensitive=True, category_id=cs_category_id)
        db.session.add(case_sensitive_challenge)
        db.session.commit()
        case_sensitive_challenge_id = case_sensitive_challenge.id # Get ID here
        case_sensitive_challenge_points = case_sensitive_challenge.points # Get points here

    # Get a test client and manually log in the unique user
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['_user_id'] = str(cs_user_id)
            session['_fresh'] = True

        # Test with correct casing
        response = client.post(f'/submit_flag/{case_sensitive_challenge_id}', data={'flag': 'CASEFLAG'})
        assert response.status_code == 200
        assert response.json['success'] == True
        assert response.json['message'] == f'Correct Flag! You earned {case_sensitive_challenge_points} points!'

        # Test with incorrect casing (should fail)
        response = client.post(f'/submit_flag/{case_sensitive_challenge_id}', data={'flag': 'caseflag'})
        assert response.status_code == 200
        assert response.json['success'] == False
        assert response.json['message'] == 'Incorrect Flag. Please try again.'