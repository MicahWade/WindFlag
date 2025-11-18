import pytest
from app import create_app
from scripts.config import TestConfig
from scripts.extensions import db, bcrypt
from scripts.models import User, Category, Challenge

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
