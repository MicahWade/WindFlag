import re
from playwright.sync_api import Page, expect
import pytest
from scripts.models import User, Challenge, Submission
from scripts.extensions import db, bcrypt
from flask import url_for
from datetime import datetime, UTC

# Helper function to get a seeded object from the database
def get_seeded_object(app, model, obj_id):
    with app.app_context():
        return db.session.get(model, obj_id)

# Helper function for login
def login(page: Page, username, password):
    page.goto("/login")
    page.fill("input[name='username']", username)
    page.fill("input[name='password']", password)
    page.click("input[type='submit']")

# Helper function to get user from seed_data
def get_user_from_seed(seed_data, username):
    for user in seed_data['users'] + seed_data['admins']:
        if user.username == username:
            return user
    return None
