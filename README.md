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
    ```bash
    python create_db.py
    ```

3.  **Run the Application:**
    ```bash
    python app.py
    ```

4.  **Access the Application:**
    Open your web browser and go to `http://127.0.0.1:5000/`.

## Creating an Admin User

To create an admin user, you will need to register a new user and then manually set the `is_admin` flag to `True` in the database. You can use a SQLite browser to edit the `app.db` file.