import pytest
from app import create_app
from scripts.config import TestConfig
from scripts.extensions import db, bcrypt
from scripts.models import User, Category, Challenge, ChallengeFlag, Submission, FlagSubmission, MULTI_FLAG_TYPES
from datetime import datetime, UTC
import uuid # Import uuid

# Fixture from conftest.py
# @pytest.fixture(scope='function')
# def multi_flag_challenge_setup(app): ...

def test_submit_single_flag_challenge_correct(app, multi_flag_challenge_setup):
    client, user, category = multi_flag_challenge_setup
    with app.app_context():
        challenge = Challenge(name="Single Flag Test", description="Desc", points=100,
                              case_sensitive=True, category_id=category.id, multi_flag_type='SINGLE')
        db.session.add(challenge)
        db.session.commit()
        flag = ChallengeFlag(challenge_id=challenge.id, flag_content="SINGLEFLAG")
        db.session.add(flag)
        db.session.commit()

        response = client.post(f'/submit_flag/{challenge.id}', data={'flag': 'SINGLEFLAG'})
        assert response.status_code == 200
        assert response.json['success'] == True
        assert "Challenge Solved!" in response.json['message']
        
        # Verify submission and score
        assert Submission.query.filter_by(user_id=user.id, challenge_id=challenge.id).first() is not None
        assert FlagSubmission.query.filter_by(user_id=user.id, challenge_flag_id=flag.id).first() is not None
        user = User.query.get(user.id) # Re-query user to attach to current session
        assert user.score == 100

def test_submit_single_flag_challenge_incorrect(app, multi_flag_challenge_setup):
    client, user, category = multi_flag_challenge_setup
    with app.app_context():
        challenge = Challenge(name="Single Flag Test Incorrect", description="Desc", points=100,
                              case_sensitive=True, category_id=category.id, multi_flag_type='SINGLE')
        db.session.add(challenge)
        db.session.commit()
        flag = ChallengeFlag(challenge_id=challenge.id, flag_content="SINGLEFLAG")
        db.session.add(flag)
        db.session.commit()

        response = client.post(f'/submit_flag/{challenge.id}', data={'flag': 'WRONGFLAG'})
        assert response.status_code == 200
        assert response.json['success'] == False
        assert "Incorrect Flag" in response.json['message']
        
        # Verify no submission and no score change
        assert Submission.query.filter_by(user_id=user.id, challenge_id=challenge.id).first() is None
        assert FlagSubmission.query.filter_by(user_id=user.id, challenge_flag_id=flag.id).first() is None
        user = User.query.get(user.id) # Re-query user to attach to current session
        assert user.score == 0

def test_submit_any_type_challenge_correct_one_of_two(app, multi_flag_challenge_setup):
    client, user, category = multi_flag_challenge_setup
    with app.app_context():
        challenge = Challenge(name="Any Type Test", description="Desc", points=100,
                              case_sensitive=True, category_id=category.id, multi_flag_type='ANY')
        db.session.add(challenge)
        db.session.commit()
        flag1 = ChallengeFlag(challenge_id=challenge.id, flag_content="ANYFLAG1")
        flag2 = ChallengeFlag(challenge_id=challenge.id, flag_content="ANYFLAG2")
        db.session.add_all([flag1, flag2])
        db.session.commit()

        response = client.post(f'/submit_flag/{challenge.id}', data={'flag': 'ANYFLAG1'})
        assert response.status_code == 200
        assert response.json['success'] == True
        assert "Challenge Solved!" in response.json['message']
        
        # Verify submission and score
        assert Submission.query.filter_by(user_id=user.id, challenge_id=challenge.id).first() is not None
        assert FlagSubmission.query.filter_by(user_id=user.id, challenge_flag_id=flag1.id).first() is not None
        assert FlagSubmission.query.filter_by(user_id=user.id, challenge_flag_id=flag2.id).first() is None # Only one flag submitted
        user = User.query.get(user.id) # Re-query user to attach to current session
        assert user.score == 100

def test_submit_all_type_challenge_partial_then_complete(app, multi_flag_challenge_setup):
    client, user, category = multi_flag_challenge_setup
    with app.app_context():
        challenge = Challenge(name="All Type Test", description="Desc", points=100,
                              case_sensitive=True, category_id=category.id, multi_flag_type='ALL')
        db.session.add(challenge)
        db.session.commit()
        flag1 = ChallengeFlag(challenge_id=challenge.id, flag_content="ALLFLAG1")
        flag2 = ChallengeFlag(challenge_id=challenge.id, flag_content="ALLFLAG2")
        db.session.add_all([flag1, flag2])
        db.session.commit()

        # Submit first flag
        response = client.post(f'/submit_flag/{challenge.id}', data={'flag': 'ALLFLAG1'})
        assert response.status_code == 200
        assert response.json['success'] == True
        assert "submitted 1 of 2 flags" in response.json['message']
        assert Submission.query.filter_by(user_id=user.id, challenge_id=challenge.id).first() is None # Not yet solved
        assert FlagSubmission.query.filter_by(user_id=user.id, challenge_flag_id=flag1.id).first() is not None
        user = User.query.get(user.id) # Re-query user to attach to current session
        assert user.score == 0 # No score yet

        # Submit second flag
        response = client.post(f'/submit_flag/{challenge.id}', data={'flag': 'ALLFLAG2'})
        assert response.status_code == 200
        assert response.json['success'] == True
        assert "Challenge Solved!" in response.json['message']
        
        # Verify submission and score
        assert Submission.query.filter_by(user_id=user.id, challenge_id=challenge.id).first() is not None
        assert FlagSubmission.query.filter_by(user_id=user.id, challenge_flag_id=flag1.id).first() is not None
        assert FlagSubmission.query.filter_by(user_id=user.id, challenge_flag_id=flag2.id).first() is not None
        user = User.query.get(user.id) # Re-query user to attach to current session
        assert user.score == 100

def test_submit_n_of_m_type_challenge_partial_then_complete(app, multi_flag_challenge_setup):
    client, user, category = multi_flag_challenge_setup
    with app.app_context():
        challenge = Challenge(name="N of M Type Test", description="Desc", points=100,
                              case_sensitive=True, category_id=category.id, multi_flag_type='N_OF_M', multi_flag_threshold=2)
        db.session.add(challenge)
        db.session.commit()
        flag1 = ChallengeFlag(challenge_id=challenge.id, flag_content="NofMFLAG1")
        flag2 = ChallengeFlag(challenge_id=challenge.id, flag_content="NofMFLAG2")
        flag3 = ChallengeFlag(challenge_id=challenge.id, flag_content="NofMFLAG3")
        db.session.add_all([flag1, flag2, flag3])
        db.session.commit()

        # Submit first flag (1 of 3, need 2)
        response = client.post(f'/submit_flag/{challenge.id}', data={'flag': 'NofMFLAG1'})
        assert response.status_code == 200
        assert response.json['success'] == True
        assert "submitted 1 of 3 flags" in response.json['message']
        assert Submission.query.filter_by(user_id=user.id, challenge_id=challenge.id).first() is None
        user = User.query.get(user.id) # Re-query user to attach to current session
        assert user.score == 0

        # Submit second flag (2 of 3, need 2 - should solve)
        response = client.post(f'/submit_flag/{challenge.id}', data={'flag': 'NofMFLAG2'})
        assert response.status_code == 200
        assert response.json['success'] == True
        assert "Challenge Solved!" in response.json['message']
        
        # Verify submission and score
        assert Submission.query.filter_by(user_id=user.id, challenge_id=challenge.id).first() is not None
        assert FlagSubmission.query.filter_by(user_id=user.id, challenge_flag_id=flag1.id).first() is not None
        assert FlagSubmission.query.filter_by(user_id=user.id, challenge_flag_id=flag2.id).first() is not None
        assert FlagSubmission.query.filter_by(user_id=user.id, challenge_flag_id=flag3.id).first() is None
        user = User.query.get(user.id) # Re-query user to attach to current session
        assert user.score == 100

def test_submit_flag_already_submitted(app, multi_flag_challenge_setup):
    client, user, category = multi_flag_challenge_setup
    with app.app_context():
        challenge = Challenge(name="Already Submitted Test", description="Desc", points=100,
                              case_sensitive=True, category_id=category.id, multi_flag_type='ALL')
        db.session.add(challenge)
        db.session.commit()
        # Add multiple flags so that submitting one doesn't solve the challenge
        flag1 = ChallengeFlag(challenge_id=challenge.id, flag_content="DUPEFLAG1")
        flag2 = ChallengeFlag(challenge_id=challenge.id, flag_content="DUPEFLAG2")
        db.session.add_all([flag1, flag2])
        db.session.commit()

        # First submission of DUPEFLAG1
        response = client.post(f'/submit_flag/{challenge.id}', data={'flag': 'DUPEFLAG1'})
        assert response.json['success'] == True
        assert "submitted 1 of 2 flags" in response.json['message'] # Should not be solved yet
        assert FlagSubmission.query.filter_by(user_id=user.id, challenge_flag_id=flag1.id).first() is not None

        # Second submission of the same flag DUPEFLAG1
        response = client.post(f'/submit_flag/{challenge.id}', data={'flag': 'DUPEFLAG1'})
        assert response.json['success'] == False
        assert "already submitted this specific flag" in response.json['message']

def test_submit_flag_challenge_already_solved(app, multi_flag_challenge_setup):
    client, user, category = multi_flag_challenge_setup
    with app.app_context():
        challenge = Challenge(name="Already Solved Test", description="Desc", points=100,
                              case_sensitive=True, category_id=category.id, multi_flag_type='SINGLE')
        db.session.add(challenge)
        db.session.commit()
        flag = ChallengeFlag(challenge_id=challenge.id, flag_content="SOLVEDFLAG")
        db.session.add(flag)
        db.session.commit()

        # Solve the challenge first
        response = client.post(f'/submit_flag/{challenge.id}', data={'flag': 'SOLVEDFLAG'})
        assert response.json['success'] == True
        assert Submission.query.filter_by(user_id=user.id, challenge_id=challenge.id).first() is not None

        # Try to submit again
        response = client.post(f'/submit_flag/{challenge.id}', data={'flag': 'SOLVEDFLAG'})
        assert response.json['success'] == False
        assert "already solved this challenge" in response.json['message']

def test_submit_flag_case_insensitivity(app, multi_flag_challenge_setup):
    client, user, category = multi_flag_challenge_setup
    with app.app_context():
        # Case sensitive challenge
        challenge_cs = Challenge(name="Case Sensitive", description="Desc", points=100,
                                 case_sensitive=True, category_id=category.id, multi_flag_type='SINGLE')
        db.session.add(challenge_cs)
        db.session.commit()
        flag_cs = ChallengeFlag(challenge_id=challenge_cs.id, flag_content="CASEFLAG")
        db.session.add(flag_cs)
        db.session.commit()

        # Case insensitive challenge
        challenge_ci = Challenge(name="Case Insensitive", description="Desc", points=100,
                                 case_sensitive=False, category_id=category.id, multi_flag_type='SINGLE')
        db.session.add(challenge_ci)
        db.session.commit()
        flag_ci = ChallengeFlag(challenge_id=challenge_ci.id, flag_content="NOCASEFLAG")
        db.session.add(flag_ci)
        db.session.commit()

        # Test case sensitive challenge: incorrect casing should fail
        response = client.post(f'/submit_flag/{challenge_cs.id}', data={'flag': 'caseflag'})
        assert response.json['success'] == False
        assert "Incorrect Flag" in response.json['message']

        # Test case sensitive challenge: correct casing should pass
        response = client.post(f'/submit_flag/{challenge_cs.id}', data={'flag': 'CASEFLAG'})
        assert response.json['success'] == True
        assert "Challenge Solved!" in response.json['message']

        # Test case insensitive challenge: lowercase should pass
        response = client.post(f'/submit_flag/{challenge_ci.id}', data={'flag': 'nocaseflag'})
        assert response.json['success'] == True
        assert "Challenge Solved!" in response.json['message']
        
        # Test case insensitive challenge: mixed casing should pass (but challenge is already solved)
        response = client.post(f'/submit_flag/{challenge_ci.id}', data={'flag': 'NOCASEFLAG'})
        assert response.json['success'] == False # Already solved
        assert "already solved this challenge" in response.json['message']
