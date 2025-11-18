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
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as client:
        yield client

from scripts.seed import seed_database

@pytest.fixture(scope='session')
def seed_data(app):
    with app.app_context():
        return seed_database()