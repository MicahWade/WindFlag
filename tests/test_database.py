import pytest
from app import create_app
from scripts.extensions import db
from scripts.config import TestConfig

@pytest.fixture(scope='module')
def test_client():
    """
    Configures the Flask app for testing and provides a test client.
    Uses the TestConfig to ensure a dedicated test database.
    """
    app = create_app(config_class=TestConfig)
    with app.app_context():
        db.drop_all()  # Ensure a clean slate before creating tables
        db.create_all()
        yield app.test_client()
        # Drop all tables after tests are done
        db.drop_all()

def test_database_connection_and_schema_creation(test_client):
    """
    Verifies that the database can be connected to and that schema creation works.
    This test implicitly covers both SQLite and PostgreSQL based on the configuration.
    """
    # If db.create_all() and db.drop_all() in the fixture run without error,
    # then the connection and schema creation are successful.
    # We can add a simple assertion here to make the test explicit.
    # For example, check if a table exists (though direct table existence check
    # in an ORM-agnostic way is complex, successful db.create_all is enough).
    # We can try to query a model, which would fail if tables weren't created.
    from scripts.models import User
    assert db.session.query(User).first() is None
