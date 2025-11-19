# WindFlag

WindFlag: A lightweight, self-hostable CTF platform built with Flask and Tailwind CSS.

## Features

*   **User Authentication**: Secure registration, login, and logout.
*   **Challenge Management**: Create, update, and delete challenges with various flag types (single, any, all, N of M).
*   **Category Management**: Organize challenges into categories.
*   **Scoreboard**: Dynamic scoreboard with user rankings and points.
*   **Admin Panel**: Comprehensive administration interface for managing users, challenges, categories, and settings.
*   **Analytics Dashboard**: Visual analytics for category points, user points, challenges solved over time, fails vs. succeeds, and a user-challenge matrix.
*   **Super Admin Role**: Granular permissions for super administrators, including managing other admin accounts.
*   **Award System**: Admins can grant awards to users with customizable categories and points.
*   **YAML Challenge Import**: Easily import challenges from a structured YAML file.
*   **Responsive Design**: Built with Tailwind CSS for a modern and responsive user interface.

## How to Run

1.  **Install Dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Configure Environment Variables:**
    Copy the `.env.template` file to `.env` and fill in the values. For more information, see [ENV.md](ENV.md).

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

Challenges can be imported from a YAML file using the `-yaml` or `-y` command-line argument. Users can be imported from a JSON file using `-users` or `-u`. Data can also be exported to YAML using `-export-yaml` or `-e`. For details on the YAML/JSON formats and usage for import and export, refer to [yaml.md](yaml.md).


## Testing

To run the automated tests, use the `run_tests.py` script. This will start the application in test mode and run the unit and end-to-end tests.

```bash
python run_tests.py
```

## Environment Variables

For information on environment variables, see [ENV.md](ENV.md).