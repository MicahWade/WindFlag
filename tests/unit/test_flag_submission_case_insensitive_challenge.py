import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app import create_app
from scripts.config import TestConfig # Import TestConfig
from scripts.extensions import db, bcrypt # Import db and bcrypt
from scripts.models import User, Category, Challenge, ChallengeFlag # Import models
import uuid # Import uuid

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
        # Create a test category with a unique name
        category = Category.query.filter_by(name="Insensitive Category").first()
        if not category:
            category = Category(name=f"Insensitive Category {uuid.uuid4()}") # Use UUID for unique category name
            db.session.add(category)
            db.session.commit()
        category_id = category.id

        # Create a case-insensitive challenge
        case_insensitive_challenge = Challenge(name="Case Insensitive Challenge", description="This is a case insensitive challenge.",
                                               points=100, case_sensitive=False, category_id=category_id,
                                               multi_flag_type='SINGLE') # Updated
        db.session.add(case_insensitive_challenge)
        db.session.commit()
        # Add the flag for this challenge
        ci_flag = ChallengeFlag(challenge_id=case_insensitive_challenge.id, flag_content="INSENSITIVEFLAG") # Updated
        db.session.add(ci_flag)
        db.session.commit()

        case_insensitive_challenge_id = case_insensitive_challenge.id
        case_insensitive_challenge_points = case_insensitive_challenge.points

    # Test with lowercase flag
    response = client.post(f'/submit_flag/{case_insensitive_challenge_id}', data={'flag': 'insensitiveflag'})
    assert response.status_code == 200
    assert response.json['success'] == True
    assert response.json['message'] == f'Correct Flag! Challenge Solved! You earned {case_insensitive_challenge_points} points!' # Updated message

    # Test with mixed case flag (should also succeed)
    response = client.post(f'/submit_flag/{case_insensitive_challenge_id}', data={'flag': 'InSeNsItIvEfLaG'})
    assert response.status_code == 200
    assert response.json['success'] == False # Should be false because already solved
    assert response.json['message'] == 'You have already solved this challenge!'