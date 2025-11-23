# WindFlag

WindFlag: A lightweight, self-hostable CTF platform built with Flask and Tailwind CSS.

## Features

*   **User Authentication**: Secure registration, login, and logout.
*   **Challenge Management**: Create, update, and delete challenges with various flag types (single, any, all, N of M).
*   **Category Management**: Organize challenges into categories.
*   **Scoreboard**: Dynamic scoreboard with user rankings and points.
*   **Configurable Point Decay**: Set challenges to have static, linear, or logarithmic point decay, with configurable minimum points and proactive decay options.
*   **Admin Panel**: Comprehensive administration interface for managing users, challenges, categories, and settings.
*   **Analytics Dashboard**: Visual analytics for category points, user points, challenges solved over time, fails vs. succeeds, and a user-challenge matrix.
*   **Super Admin Role**: Granular permissions for super administrators, including managing other admin accounts.
*   **Award System**: Admins can grant awards to users with customizable categories and points.
*   **YAML Challenge Import/Export**: Easily import and export challenges, including associated hints, from a structured YAML file.
*   **Responsive Design**: Built with Tailwind CSS for a modern and responsive user interface.
*   **Code Editor (CodeMirror)**: Integrated a powerful in-browser code editor (CodeMirror) for coding challenges, featuring syntax highlighting for Bash, Dart, Haskell, JavaScript (Node), PHP, and Python, and themes.

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

## Testing

To run the automated tests, use the `run_tests.py` script. This will start the application in test mode and run the unit and end-to-end tests.

## Environment Variables

For information on environment variables, see [ENV.md](ENV.md).