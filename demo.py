import multiprocessing
from app import create_app
import time
import os

from scripts.config import TestConfig

TEST_SERVER_PORT = 5001

from scripts.extensions import db
from scripts.seed import seed_database
import argparse # Keep argparse for the --time argument

DB_FILE_PATH = 'instance/test.db'

def _delete_db_file():
    if os.path.exists(DB_FILE_PATH):
        os.remove(DB_FILE_PATH)
        print(f"Deleted existing database file: {DB_FILE_PATH}")

# Function to run the Flask app for demo mode
def run_demo_server(port, debug_mode, time_duration=None):
    _delete_db_file() # Ensure clean database for demo
    app = create_app(config_class=TestConfig)
    
    # Existing code for seeding and running the app
    with app.app_context():
        db.create_all()
        seed_database() # Seed database for demo mode
    
    # Start the Flask app in a separate process
    server_process = multiprocessing.Process(target=app.run, kwargs={'debug': debug_mode, 'host': '0.0.0.0', 'port': port})
    server_process.start()

    if time_duration:
        print(f"Demo server will shut down in {time_duration} seconds.")
        time.sleep(time_duration)
        server_process.terminate()
        server_process.join()
        print("Demo server shut down automatically.")
    else:
        print(f"Demo server running indefinitely on http://127.0.0.1:{port}. Press Ctrl+C to stop.")
        server_process.join() # Wait for the server process to terminate (e.g., via Ctrl+C)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the WindFlag server in demo mode with test data.')
    parser.add_argument('-t', '--time', type=int,
                        help='Duration in seconds to run the demo server before shutting down automatically.')
    args = parser.parse_args()

    run_demo_server(TEST_SERVER_PORT, True, args.time)
