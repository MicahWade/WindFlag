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

## Test Mode

You can run the application in test mode using the `-test` flag. In this mode, the application will use a separate database (`test_mode.db`) and will automatically shut down after a specified timeout.

```bash
# Run in test mode with default 30-minute timeout (1800 seconds)
python app.py -test

# Run in test mode with a custom timeout of 10 seconds
python app.py -test 10
```

## Environment Variables

For information on environment variables, see [ENV.md](ENV.md).