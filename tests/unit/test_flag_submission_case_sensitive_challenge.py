import pytest
from app import create_app
from scripts.config import TestConfig
from scripts.extensions import db, bcrypt
from scripts.models import User, Category, Challenge, ChallengeFlag # Import ChallengeFlag
import uuid # Import uuid

def test_flag_submission_case_sensitive_challenge(app):
    with app.app_context():
        # Create a unique test user for this test
        unique_id = uuid.uuid4()
        hashed_password = bcrypt.generate_password_hash("cs_password").decode('utf-8')
        cs_user = User(username=f"cs_testuser_{unique_id}", email=f"cs_test_{unique_id}@example.com", password_hash=hashed_password) # Use UUID for unique username and email
        db.session.add(cs_user)
        db.session.commit()
        cs_user_id = cs_user.id # Get ID here

        # Create a test category with a unique name
        cs_category = Category(name=f"CS Category {uuid.uuid4()}") # Use UUID for unique category name
        db.session.add(cs_category)
        db.session.commit()
        cs_category_id = cs_category.id # Get ID here

        # Create a case-sensitive challenge (SINGLE type)
        case_sensitive_challenge = Challenge(name="Case Sensitive Challenge", description="This is a case sensitive challenge.",
                                             points=150, case_sensitive=True, category_id=cs_category_id,
                                             multi_flag_type='SINGLE') # Updated
        db.session.add(case_sensitive_challenge)
        db.session.commit()
        # Add the flag for this challenge
        cs_flag = ChallengeFlag(challenge_id=case_sensitive_challenge.id, flag_content="CASEFLAG") # Updated
        db.session.add(cs_flag)
        db.session.commit()

        case_sensitive_challenge_id = case_sensitive_challenge.id
        case_sensitive_challenge_points = case_sensitive_challenge.points

    # Get a test client and manually log in the unique user
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['_user_id'] = str(cs_user_id)
            session['_fresh'] = True

        # Test with incorrect casing (should fail)
        # This test should only attempt to submit the incorrectly cased flag
        response = client.post(f'/submit_flag/{case_sensitive_challenge_id}', data={'flag': 'caseflag'})
        assert response.status_code == 200
        assert response.json['success'] == False
        assert response.json['message'] == 'Incorrect Flag. Please try again.'

        # Now, submit the correct flag to ensure it works
        response = client.post(f'/submit_flag/{case_sensitive_challenge_id}', data={'flag': 'CASEFLAG'})
        assert response.status_code == 200
        assert response.json['success'] == True
        assert response.json['message'] == f'Correct Flag! Challenge Solved! You earned {case_sensitive_challenge_points} points!'