# WindFlag

WindFlag: A lightweight, self-hostable CTF platform built with Flask and Tailwind CSS.

## How to Run

1.  **Install Dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Configure Environment Variables:**
    Copy the `.env.template` file to `.env` and fill in the values. For more information, see [ENV.md](ENV.md).

3.  **Create the Database:**
    ```bash
    python create_db.py
    ```

4.  **Run the Application:**
    ```bash
    python app.py
    ```

5.  **Access the Application:**
    Open your web browser and go to `http://127.0.0.1:5000/`.

## Creating an Admin User

You can create an admin user with the `-admin` flag when running the application:

```bash
python app.py -admin <email> <password>
```

Alternatively, you can manually create a user and set the `is_admin` flag to `True` in the database.

## Environment Variables

For information on environment variables, see [ENV.md](ENV.md).