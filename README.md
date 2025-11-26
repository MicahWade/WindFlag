# WindFlag

WindFlag: A lightweight, self-hostable CTF platform built with Flask and Tailwind CSS.

## Features

*   **User Authentication**: Secure registration, login, and logout.
*   **Challenge Management**: Comprehensive tools to create, update, and delete challenges. Supports diverse flag configurations including:
    *   **Single Flag**: A traditional CTF flag where one correct submission solves the challenge.
    *   **Any Flag**: Multiple possible correct flags; any single correct submission solves the challenge. Ideal for challenges with several valid solutions.
    *   **All Flags**: Requires submission of all predefined correct flags to solve the challenge. Useful for multi-part challenges.
    *   **N of M Flags**: Configurable where 'N' out of 'M' possible flags must be submitted to solve the challenge. Offers flexibility for challenges with partial credit or multiple paths to completion.
*   **Category Management**: Efficiently organize challenges into logical categories, improving navigation and user experience.
*   **Scoreboard**: A dynamic, real-time scoreboard displaying user rankings, points, and solve progress, fostering competitive engagement.
*   **Configurable Point Decay**: Advanced point decay models to make challenges more engaging and reward earlier solves:
    *   **Static**: Challenge points remain constant regardless of solve time.
    *   **Linear**: Points decrease linearly over time after the first solve, encouraging quick solutions.
    *   **Logarithmic**: Points decrease logarithmically, offering a gentler decay curve that still rewards early solves but less severely than linear decay.
    *   **Configurable Minimum Points**: Set a floor for challenge points, ensuring they never drop below a certain value.
    *   **Proactive Decay Options**: Implement strategies to manage point distribution and challenge difficulty dynamically.
*   **Admin Panel**: A powerful and intuitive administration interface providing granular control over the platform:
    *   **User Management**: Create, edit, and delete user accounts; assign roles (e.g., admin, super admin).
    *   **Challenge Management**: Full CRUD (Create, Read, Update, Delete) operations for challenges, including flag configuration, hints, and visibility settings.
    *   **Category Management**: Organize, create, and modify challenge categories.
    *   **Settings Management**: Configure global platform settings, themes, and system parameters.
    *   **Award Management**: Define, assign, and manage awards given to users.
*   **Analytics Dashboard**: Visual and data-driven insights into platform activity and user performance:
    *   **Category Points Distribution**: See how points are distributed across different challenge categories.
    *   **User Points Over Time**: Track individual user progress and point accumulation.
    *   **Challenges Solved Over Time**: Monitor the rate at which challenges are being solved across the platform.
    *   **Fails vs. Succeeds**: Analyze submission attempt statistics to gauge challenge difficulty.
    *   **User-Challenge Matrix**: A comprehensive overview of which users have attempted and solved which challenges.
*   **Super Admin Role**: Introduced for enhanced security and administrative hierarchy, allowing super administrators to manage other admin accounts and critical system configurations.
*   **Award System**: A flexible system for recognizing user achievements:
    *   Admins can grant custom awards to users.
    *   Awards can be assigned to customizable categories (e.g., "First Blood," "Participation").
    *   Awards can carry point values, contributing to a user's total score.
*   **YAML Challenge Import/Export**: Streamlined process for managing challenges:
    *   Easily import new challenges and their associated hints from a structured YAML file.
    *   Export existing challenges to YAML for backup or migration.
    *   Supports bulk operations, ideal for rapid challenge deployment.
*   **Responsive Design**: Crafted with Tailwind CSS to ensure a modern, accessible, and adaptive user interface across all devices and screen sizes.
*   **Code Editor (CodeMirror)**: An integrated, feature-rich in-browser code editor designed for coding challenges:
    *   **Syntax Highlighting**: Supports a wide range of languages including Bash, Dart, Haskell, JavaScript (Node), PHP, and Python.
    *   **Themes**: Customizable editor themes to suit user preferences.
    *   **Interactive Coding**: Provides a comfortable environment for users to write and test code snippets directly within the platform.

## How to Run

1.  **Install Dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Configure Environment Variables:**
    Copy the `.env.template` file to `.env` and fill in the values. For more information, see [ENV.md](docs/ENV.md).

3.  **Run the Application:**
    The default database (`app.db`) will be created automatically if it doesn't exist.
    ```bash
    python app.py
    ```

4.  **Access the Application:**
    Open your web browser and go to `http://127.0.0.1:5000/`.

## Redis Caching Setup (Optional)

WindFlag supports optional Redis caching to improve performance for frequently accessed data. To enable and configure Redis caching:

1.  **Install Redis Server:**
    *   **Ubuntu/Debian:**
        ```bash
        sudo apt update
        sudo apt install redis-server
        ```
    *   **macOS (using Homebrew):**
        ```bash
        brew install redis
        ```
    *   For other operating systems, please refer to the [official Redis documentation](https://redis.io/docs/getting-started/installation/).

2.  **Start Redis Server:**
    *   **Ubuntu/Debian:**
        ```bash
        sudo systemctl start redis-server
        sudo systemctl enable redis-server # To start Redis automatically on boot
        ```
    *   **macOS (using Homebrew):**
        ```bash
        brew services start redis
        ```
    *   You can verify Redis is running by executing `redis-cli ping`. It should return `PONG`.

3.  **Configure WindFlag to Use Redis:**
    Open your `.env` file (created from `.env.template`) and add/modify the following variables:
    ```
    # Enable Redis caching (set to True to activate)
    ENABLE_REDIS_CACHE=True

    # Redis connection URL (default is usually fine for local development)
    # If your Redis server is on a different host or port, adjust this value.
    REDIS_URL=redis://localhost:6379/0
    ```
    Ensure `ENABLE_REDIS_CACHE` is set to `True` for caching to be active. The `REDIS_URL` should point to your running Redis instance.

With Redis running and configured, WindFlag will automatically utilize the cache for various data lookups and API responses, significantly improving performance.

## Creating an Admin User

You can create an admin user with the `-admin` flag when running the application:

```bash
python app.py -admin <username> <password>
```

Alternatively, you can manually create a user and set the `is_admin` flag to `True` in the database.

## Importing and Exporting Data via YAML/JSON

Challenges can be imported from a YAML file using the `-yaml` or `-y` command-line argument. Users can be imported from a JSON file using `-users` or `-u`. Data can also be exported to YAML using `-export-yaml` or `-e`. For details on the YAML/JSON formats and usage for import and export, refer to [yaml.md](docs/yaml.md).

## Admin Documentation

For detailed information on admin-specific features, including challenge visibility and management, refer to [admin.md](docs/admin.md).

### Admin Challenge Stripes

For administrators, challenges on the `/challenges` page display colored stripes to quickly convey their status based on unlock conditions and user solve rates. These stripes follow a specific precedence: Red > Orange > Yellow > Blue.

*   **Red Stripe ("Locked")**:
    *   **Condition**: The challenge itself is hidden (`is_hidden = True`), its category is hidden, or it has a timed unlock in the future.
    *   **Meaning**: The challenge is currently inaccessible to regular users due to explicit hiding or a future unlock date.

*   **Orange Stripe ("Unlockable (No Solves)")**:
    *   **Condition**: Not Red, has prerequisites (e.g., percentage, count, or specific challenges), is not timed-locked (or its timed unlock has passed), and 0% of eligible users have unlocked it.
    *   **Meaning**: The challenge is visible but no regular user has yet met its prerequisites to unlock it.

*   **Yellow Stripe ("Unlocked (0-50%)")**:
    *   **Condition**: Not Red, not Orange, and more than 0% but less than or equal to 50% of eligible users have unlocked it.
    *   **Meaning**: The challenge is unlocked for some users, but it's still relatively rare or new.

*   **Blue Stripe ("Rarely Unlocked (50-90%)")**:
    *   **Condition**: Not Red, not Orange, not Yellow, and more than 50% but less than or equal to 90% of eligible users have unlocked it.
    *   **Meaning**: The challenge is unlocked for a significant portion of users, but not yet widely solved.

*   **No Stripe**:
    *   **Condition**: Not Red, Orange, Yellow, or Blue. This typically means the challenge is unlocked for more than 90% of eligible users, or it has no special unlock conditions and is generally available.
    *   **Meaning**: The challenge is widely accessible and/or commonly solved.

## Project Structure

The WindFlag project is organized into several key directories, each serving a specific purpose to maintain modularity and ease of development.

*   **`app.py`**: The main application entry point, responsible for initializing the Flask app, database, and registering blueprints.
*   **`config.py`**: Handles application configuration settings, including secret keys, database URI, and other environment-dependent variables.
*   **`static/`**: Contains all static assets such as CSS stylesheets, JavaScript files, images, and fonts.
    *   **`static/css/`**: Stores CSS files for styling the application.
    *   **`static/js/`**: Houses JavaScript files for front-end interactivity.
    *   **`static/icon/`**: Contains favicon and other site icons.
    *   **`static/themes/`**: Directory for different UI themes, each with its own assets.
*   **`templates/`**: Holds Jinja2 HTML templates used to render dynamic web pages.
    *   **`templates/admin/`**: Templates specific to the administration panel.
    *   **`templates/docs/`**: Templates for dynamically generated documentation or specialized content.
*   **`scripts/`**: Contains Python scripts for various backend functionalities, API routes, and utility functions.
    *   **`scripts/models.py`**: Defines the SQLAlchemy database models for the application's data structures.
    *   **`scripts/routes.py`**: (Or similar, e.g., `api_routes.py`, `admin_routes.py`) Defines the URL routes and their corresponding view functions.
    *   **`scripts/forms.py`**: Contains Flask-WTF form definitions for input validation.
    *   **`scripts/utils.py`**: General utility functions used across the application.
    *   **`scripts/extensions.py`**: Initializes and manages Flask extensions like SQLAlchemy, Bcrypt, etc.
*   **`docs/`**: Markdown documentation files providing detailed information on various aspects of the platform.
    *   **`docs/API/`**: Documentation specifically for the platform's API endpoints.
*   **`.venv/`**: (Hidden) Virtual environment for Python dependencies.
*   **`tests/`**: Contains unit and integration tests for the application.
*   **`.env`**: (Hidden) Environment variables for local development (not committed to version control).
*   **`.env.template`**: A template file for setting up `.env`.

## Contribution Guidelines

We welcome contributions to WindFlag! If you're looking to contribute, please follow these guidelines:

### How to Contribute

1.  **Fork the Repository**: Start by forking the WindFlag repository to your GitHub account.
2.  **Clone Your Fork**: Clone your forked repository to your local machine.
    ```bash
    git clone https://github.com/your-username/WindFlag.git
    cd WindFlag
    ```
3.  **Create a New Branch**: Create a new branch for your feature or bug fix.
    ```bash
    git checkout -b feature/your-feature-name
    ```
    or
    ```bash
    git checkout -b bugfix/issue-description
    ```
4.  **Make Your Changes**: Implement your feature, fix the bug, or improve the documentation.
    *   Adhere to the existing code style.
    *   Write clear, concise, and well-commented code.
    *   Add unit or integration tests for new features or bug fixes, if applicable.
5.  **Test Your Changes**: Ensure that your changes do not introduce new bugs and that all existing tests pass.
    ```bash
    python run_tests.py
    ```
6.  **Commit Your Changes**: Write clear and descriptive commit messages.
    ```bash
    git commit -m "feat: Add new awesome feature"
    ```
    or
    ```bash
    git commit -m "fix: Resolve #123 - bug description"
    ```
7.  **Push to Your Fork**: Push your local branch to your forked repository on GitHub.
    ```bash
    git push origin feature/your-feature-name
    ```
8.  **Create a Pull Request (PR)**:
    *   Go to the original WindFlag repository on GitHub.
    *   You should see an option to create a new pull request from your recently pushed branch.
    *   Provide a clear title and detailed description of your changes in the PR.
    *   Reference any related issues.

### Code Style

*   Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code.
*   For JavaScript, adhere to a consistent style, ideally similar to [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript).
*   For CSS, try to follow a consistent, readable format.

### Reporting Bugs

If you find a bug, please open an issue on GitHub. Include:
*   A clear and concise description of the bug.
*   Steps to reproduce the behavior.
*   Expected behavior.
*   Screenshots or videos if applicable.
*   Your operating system and browser.

### Feature Requests

For feature requests, open an issue on GitHub. Describe:
*   The feature you'd like to see.
*   Why it's important or useful.
*   Any potential solutions or ideas you have.

## Testing

To run the automated tests, use the `run_tests.py` script. This will start the application in test mode and run the unit and end-to-end tests.

## Environment Variables

For information on environment variables, see [ENV.md](ENV.md).