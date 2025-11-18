import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app import create_app
from scripts.extensions import db, bcrypt
from scripts.models import User
from flask import url_for

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # Use in-memory SQLite for testing
        "WTF_CSRF_ENABLED": False # Disable CSRF for easier testing
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_user(app):
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash("adminpass").decode('utf-8')
        admin = User(username="admin", email="admin@example.com", password_hash=hashed_password, is_admin=True, hidden=True)
        db.session.add(admin)
        db.session.commit()
        return admin

@pytest.fixture
def regular_user(app):
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash("userpass").decode('utf-8')
        user = User(username="testuser", email="user@example.com", password_hash=hashed_password, is_admin=False, hidden=False)
        db.session.add(user)
        db.session.commit()
        return user

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_admin_can_access_manage_users(client, admin_user):
    login(client, admin_user.username, "adminpass")
    response = client.get('/admin/users')
    assert response.status_code == 200
    assert b"Manage Users" in response.data

def test_non_admin_cannot_access_manage_users(client, regular_user):
    login(client, regular_user.username, "userpass")
    response = client.get('/admin/users', follow_redirects=True)
    assert response.status_code == 200
    assert b"You do not have permission to access this page." in response.data

def test_toggle_user_hidden_status(client, admin_user, regular_user):
    login(client, admin_user.username, "adminpass")

    # Initially, regular_user is not hidden
    with client.application.app_context():
        user = User.query.get(regular_user.id)
        assert user.hidden is False

    # Toggle hidden status
    response = client.post(f'/admin/user/{regular_user.id}/toggle_hidden', follow_redirects=True)
    assert response.status_code == 200
    assert f"User {regular_user.username} hidden status toggled to True.".encode() in response.data

    with client.application.app_context():
        user = User.query.get(regular_user.id)
        assert user.hidden is True

    # Toggle back to not hidden
    response = client.post(f'/admin/user/{regular_user.id}/toggle_hidden', follow_redirects=True)
    assert response.status_code == 200
    assert f"User {regular_user.username} hidden status toggled to False.".encode() in response.data

    with client.application.app_context():
        user = User.query.get(regular_user.id)
        assert user.hidden is False

def test_toggle_user_admin_status(client, admin_user, regular_user):
    login(client, admin_user.username, "adminpass")

    # Initially, regular_user is not admin and not hidden
    with client.application.app_context():
        user = User.query.get(regular_user.id)
        assert user.is_admin is False
        assert user.hidden is False

    # Make user admin
    response = client.post(f'/admin/user/{regular_user.id}/toggle_admin', follow_redirects=True)
    assert response.status_code == 200
    assert f"User {regular_user.username} admin status toggled to True.".encode() in response.data

    with client.application.app_context():
        user = User.query.get(regular_user.id)
        assert user.is_admin is True
        assert user.hidden is True # Should be hidden when made admin

    # Revoke admin status
    response = client.post(f'/admin/user/{regular_user.id}/toggle_admin', follow_redirects=True)
    assert response.status_code == 200
    assert f"User {regular_user.username} admin status toggled to False.".encode() in response.data

    with client.application.app_context():
        user = User.query.get(regular_user.id)
        assert user.is_admin is False
        # Hidden status should remain True unless explicitly changed
        assert user.hidden is True

def test_admin_cannot_change_own_admin_status(client, admin_user):
    login(client, admin_user.username, "adminpass")
    response = client.post(f'/admin/user/{admin_user.id}/toggle_admin', follow_redirects=True)
    assert response.status_code == 200
    assert b"You cannot change your own admin status." in response.data

def test_hidden_user_not_on_scoreboard(client, admin_user, regular_user):
    # Ensure regular_user is not hidden initially
    with client.application.app_context():
        user = User.query.get(regular_user.id)
        user.hidden = False
        db.session.commit()

    # Log in as admin to access scoreboard (scoreboard requires login)
    login(client, admin_user.username, "adminpass")

    # Check scoreboard data - regular_user should be visible
    response = client.get('/api/scoreboard_data')
    assert response.status_code == 200
    data = response.get_json()
    usernames_on_scoreboard = [u['username'] for u in data['all_players_ranked']]
    assert regular_user.username in usernames_on_scoreboard

    # Make regular_user hidden
    client.post(f'/admin/user/{regular_user.id}/toggle_hidden', follow_redirects=True)

    # Check scoreboard data again - regular_user should NOT be visible
    response = client.get('/api/scoreboard_data')
    assert response.status_code == 200
    data = response.get_json()
    usernames_on_scoreboard = [u['username'] for u in data['all_players_ranked']]
    assert regular_user.username not in usernames_on_scoreboard

    # Admin should still be able to see the hidden user in manage users page
    response = client.get('/admin/users')
    assert response.status_code == 200
    assert regular_user.username.encode() in response.data
    assert b"Yes" in response.data # Hidden status should be 'Yes' for regular_user
