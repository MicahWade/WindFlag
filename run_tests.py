import pytest
import multiprocessing
from app import create_app
import sys
import time

from scripts.config import TestConfig # Added import

TEST_SERVER_PORT = 5001 # Define a specific port for the test server

from scripts.extensions import db # Added import

from scripts.seed import seed_database
import argparse

def run_app():
    app = create_app(config_class=TestConfig) # Modified to use TestConfig
    with app.app_context(): # Added app context
        db.create_all() # Create tables for the server process
    app.run(debug=False, host='0.0.0.0', port=TEST_SERVER_PORT, use_reloader=False) # Use TEST_SERVER_PORT

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run unit and end-to-end tests for WindFlag.')
    parser.add_argument('-d', '--demo', action='store_true',
                        help='Run the server in demo mode with test data, without running tests.')
    parser.add_argument('-p', '--playwright', action='store_true',
                        help='Run only Playwright end-to-end tests.')
    args = parser.parse_args()

    if args.demo:
        app = create_app(config_class=TestConfig)
        with app.app_context():
            db.create_all() # Create tables for demo mode
            seed_database()
        app.run(debug=True, host='0.0.0.0', port=TEST_SERVER_PORT)
    else:
        server_process = multiprocessing.Process(target=run_app)
        server_process.start()

        # Give the server a moment to start
        time.sleep(1) # Increased sleep time

        pytest_args = ['--base-url', f'http://127.0.0.1:{TEST_SERVER_PORT}']
        if args.playwright:
            pytest_args.append('tests/e2e/')
        else:
            pytest_args.append('tests/') # Run all tests in the tests directory

        # Run pytest
        exit_code = pytest.main(pytest_args)

        # Shutdown the server
        server_process.terminate()
        server_process.join()

        # Exit with the same code as pytest
        exit(exit_code)
