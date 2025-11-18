import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app import create_app
from scripts.config import TestConfig # Import TestConfig

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