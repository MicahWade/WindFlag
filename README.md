# WindFlag

WindFlag: A lightweight, self-hostable CTF platform built with Flask and Tailwind CSS.

## How to Run

1.  **Install Dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Create the Database:**
    Since migrations have been removed, you will need to create the database manually. You can do this by running the following commands in a Python shell:
    ```python
    from app import create_app, db
    app = create_app()
    with app.app_context():
        db.create_all()
    ```

3.  **Run the Application:**
    ```bash
    export FLASK_APP=app.py
    flask run
    ```
    Or, for development mode:
    ```bash
    python app.py
    ```

4.  **Access the Application:**
    Open your web browser and go to `http://127.0.0.1:5000/`.

## Creating an Admin User

To create an admin user, you will need to register a new user and then manually set the `is_admin` flag to `True` in the database. You can use a SQLite browser to edit the `app.db` file.
