# Testing Setup

This document outlines how to set up and run tests for the WindFlag application, with a focus on database testing, including PostgreSQL integration.

## 1. Install Pytest

The WindFlag application uses `pytest` for its testing framework. If you don't already have it installed, you can install it within your Python virtual environment:

```bash
pip install pytest
```

## 2. Configure for Database Testing

The application's testing configuration is managed through the `.env` file, similar to the main application. This allows you to specify a dedicated database for testing, preventing conflicts with your development or production data.

### `.env` Configuration for PostgreSQL Testing

To run tests against a PostgreSQL database:

1.  **Open your `.env` file** (located in the project root).
2.  **Ensure `USE_POSTGRES` is set to `true`**:
    ```
    USE_POSTGRES=True
    ```
3.  **Set `TEST_DATABASE_URL`**: This variable should point to a **separate PostgreSQL database** specifically for testing. It is crucial *not* to use your main application database for testing, as tests will create, modify, and drop tables.
    ```
    TEST_DATABASE_URL=postgresql://test_user:test_password@localhost:5432/test_db_name
    ```
    *   **Important**: Replace `test_user`, `test_password`, `localhost:5432`, and `test_db_name` with your actual PostgreSQL test database credentials.

### Default (SQLite) Testing

If `USE_POSTGRES` is `false` or not explicitly set to `true`, tests will default to using an SQLite database named `test.db` (located in the `instance/` folder by default).

## 3. Running Tests

Navigate to the root directory of your project in your terminal and run `pytest`:

```bash
# Ensure your virtual environment is activated
source .venv/bin/activate
pytest
```

This command will discover and execute all test files (e.g., `tests/test_*.py`).

## 4. Understanding `tests/test_database.py`

The `tests/test_database.py` file contains a basic test (`test_database_connection_and_schema_creation`) that verifies:

*   The application can be initialized successfully in a test context.
*   The database (either SQLite or PostgreSQL, depending on your `.env` configuration) can be connected to.
*   Database schema creation (`db.create_all()`) and cleanup (`db.drop_all()`) work as expected.

This test is designed to ensure that your database setup is functional for the application's ORM (SQLAlchemy). Each test run using the `test_client` fixture ensures a clean database slate by dropping and recreating all tables.
