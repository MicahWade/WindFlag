import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app import create_app
from scripts.config import TestConfig # Import TestConfig

from scripts.extensions import db
from scripts.models import User, Challenge, Submission, Category
import json

@pytest.fixture
def app():
    app = create_app(config_class=TestConfig) # Use TestConfig
    app.config.update({
        "TESTING": True,
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_challenge_solvers(client):
    # Create a user, category, and challenge
    user = User(username='testuser', password_hash='password')
    category = Category(name='Test Category')
    challenge = Challenge(name='Test Challenge', description='Test Description', points=100, flag='flag', category=category)
    db.session.add(user)
    db.session.add(category)
    db.session.add(challenge)
    db.session.commit()

    # Create a submission
    submission = Submission(user_id=user.id, challenge_id=challenge.id, score_at_submission=100)
    db.session.add(submission)
    db.session.commit()

    # Log in the user
    with client.session_transaction() as session:
        session['_user_id'] = user.id
        session['_fresh'] = True

    # Make a request to the endpoint
    response = client.get(f'/api/challenge/{challenge.id}/solvers')

    # Assert the response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['solver_count'] == 1
    assert data['solvers'] == ['testuser']