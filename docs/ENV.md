# Environment Variables

This document provides comprehensive details on the environment variables used by the WindFlag application, their purpose, and how to configure them effectively.

## `.env` File Overview

The WindFlag application leverages a `.env` file for managing configuration settings that can vary between deployment environments (e.g., development, staging, production). This approach keeps sensitive information and environment-specific settings out of version control, enhancing security and portability.

To use environment variables, create a file named `.env` in the root directory of your project. Copy the contents from `.env.template` and populate the values.

## Application Settings

These variables control general application behavior and display.

*   `APP_NAME` (string): The name of the application displayed prominently in the web interface (e.g., page titles, headers).
    *   **Default**: "WindFlag"
    *   **Example**: `APP_NAME="My Awesome CTF"`

*   `SECRET_KEY` (string): A strong, randomly generated secret key crucial for application security. It is used for cryptographic operations, including securing client-side sessions (Flask sessions). **This must be unique and kept confidential.**
    *   **Recommendation**: Generate a long, random string.
    *   **Example**: `SECRET_KEY="your_very_secret_and_long_random_key_here"`

*   `BASIC_INDEX_PAGE` (boolean): Controls the appearance of the application's home page.
    *   `true`: Displays a minimal home page with only the welcome section.
    *   `false` (or omitted): Displays the full, expanded home page, which may include additional content, dynamic elements, and graphics.
    *   **Default**: `false`
    *   **Example**: `BASIC_INDEX_PAGE=true`

*   `DISABLE_SIGNUP` (boolean): Determines whether new user registrations are permitted.
    *   `true`: New user registrations are disabled. Only existing users can log in.
    *   `false` (or omitted): New user registrations are allowed.
    *   **Default**: `false`
    *   **Example**: `DISABLE_SIGNUP=true`

## API Key Settings

These variables control API key functionality, including a special administrative key.

*   `ADMIN_API_KEY` (string, optional): A special API key that grants full administrative access to all API endpoints without requiring a specific user account. **This key bypasses regular authentication and should be kept extremely confidential.**
    *   **Recommendation**: Generate a long, random string.
    *   **Example**: `ADMIN_API_KEY="your_super_secret_admin_api_key_123"`

## User Management Settings

These variables relate to user registration and authentication processes.

*   `REQUIRE_JOIN_CODE` (boolean): If set to `true`, new users must enter a specific `JOIN_CODE` during registration.
    *   `true`: A join code is required.
    *   `false` (or omitted): No join code is needed for registration.
    *   **Default**: `false`
    *   **Example**: `REQUIRE_JOIN_CODE=true`

*   `JOIN_CODE` (string): The specific code that new users must provide if `REQUIRE_JOIN_CODE` is set to `true`. This variable is ignored if `REQUIRE_JOIN_CODE` is `false`.
    *   **Example**: `JOIN_CODE="secretctf2025"`

*   `REQUIRE_EMAIL` (boolean): Controls whether the email field is mandatory during user registration.
    *   `true` (or omitted): Email is a required field.
    *   `false`: Email is an optional field.
    *   **Default**: `true`
    *   **Example**: `REQUIRE_EMAIL=false`

*   `USERNAME_WORD_COUNT` (integer): Specifies the number of words to use when generating random usernames (e.g., for seeded users or if a feature for auto-generating usernames is enabled).
    *   **Default**: `2`
    *   **Example**: `USERNAME_WORD_COUNT=3` (e.g., "fast-blue-car")

*   `USERNAME_ADD_NUMBER` (boolean): If `true`, a random two-digit number is appended to the end of automatically generated usernames.
    *   **Default**: `true`
    *   **Example**: `USERNAME_ADD_NUMBER=false` (generates "fast-blue-car" instead of "fast-blue-car-87")

*   `PRESET_USER_COUNT` (integer): Used primarily by the seeding script (`scripts/seed.py`). Defines the number of dummy users to generate when seeding the database.
    *   **Default**: `10`
    *   **Example**: `PRESET_USER_COUNT=50`

*   `WORDS_FILE_PATH` (string): The relative or absolute path to a text file containing a list of words. These words are used by the application for generating usernames when `USERNAME_WORD_COUNT` is active. Each word should be on a new line.
    *   **Default**: `words.text` (located in the project root)
    *   **Example**: `WORDS_FILE_PATH="data/custom_words.txt"`

## Programming Language Enablement

These variables control which programming languages are enabled for coding challenges. By default, all supported languages are enabled. Disabling a language will prevent it from appearing as an option in the admin panel and from being executed in the sandboxed environment.

*   `ENABLE_PYTHON3` (boolean): Set to `true` to enable Python 3 for coding challenges.
    *   **Default**: `true`
    *   **Example**: `ENABLE_PYTHON3=false`

*   `ENABLE_NODEJS` (boolean): Set to `true` to enable Node.js for coding challenges.
    *   **Default**: `true`
    *   **Example**: `ENABLE_NODEJS=false`

*   `ENABLE_PHP` (boolean): Set to `true` to enable PHP for coding challenges.
    *   **Default**: `true`
    *   **Example**: `ENABLE_PHP=false`

*   `ENABLE_BASH` (boolean): Set to `true` to enable Bash for coding challenges.
    *   **Default**: `true`
    *   **Example**: `ENABLE_BASH=false`

*   `ENABLE_DART` (boolean): Set to `true` to enable Dart for coding challenges.
    *   **Default**: `true`
    *   **Example**: `ENABLE_DART=false`

## Database Configuration

The WindFlag application primarily uses SQLite for simplicity but can be configured to use external relational databases like PostgreSQL via environment variables.

*   `USE_POSTGRES` (boolean): If set to `true`, the application will attempt to connect to a PostgreSQL database using the `DATABASE_URL`. If `false` (or omitted), it will default to an SQLite database.
    *   **Default**: `false`
    *   **Example**: `USE_POSTGRES=true`

*   `DATABASE_URL` (string, optional): The SQLAlchemy database URI for the main application database. This variable is only used if `USE_POSTGRES` is set to `true`.
    *   **Example for PostgreSQL**: `DATABASE_URL="postgresql://user:password@host:port/database_name"`
    *   **Example for MySQL (if supported)**: `DATABASE_URL="mysql+pymysql://user:password@host:port/database_name"`

*   `TEST_DATABASE_URL` (string, optional): The SQLAlchemy database URI for the test environment. This variable is used when `USE_POSTGRES` is `true` AND the application is running in a test context (e.g., during `pytest` execution). It's crucial to use a separate database for testing to avoid data conflicts.
    *   **Example for PostgreSQL**: `TEST_DATABASE_URL="postgresql://test_user:test_password@host:port/test_database_name"`

## Development & Debugging Settings

These variables are typically used during development.

*   `FLASK_ENV` (string): Sets the Flask environment.
    *   `development`: Enables debugging, reloader, and potentially less strict error handling.
    *   `production`: Optimizes for performance and security.
    *   **Default**: (Usually inferred or set by how Flask is run)
    *   **Example**: `FLASK_ENV=development`

*   `FLASK_DEBUG` (boolean): Enables or disables Flask's debug mode.
    *   `true`: Enables debug mode, providing detailed error messages in the browser and an interactive debugger. **Never use in production.**
    *   `false`: Disables debug mode.
    *   **Default**: (Inferred from `FLASK_ENV`)
    *   **Example**: `FLASK_DEBUG=true`

## Best Practices for `.env` Files

1.  **Never Commit `.env` to Version Control**: The `.env` file should be listed in your `.gitignore` to prevent it from being accidentally committed to Git. It often contains sensitive information like `SECRET_KEY` and `JOIN_CODE`.
2.  **Use `.env.template`**: Provide a `.env.template` (as WindFlag does) that outlines all possible environment variables without their values. This helps new developers or deployers understand what variables are needed.
3.  **Secure Your `.env` File**: Ensure that the `.env` file on your server has restricted file system permissions to prevent unauthorized access.
4.  **Restart Application on Changes**: Most applications (including Flask) require a restart to pick up changes made to the `.env` file.
