import pytest
import multiprocessing
from app import create_app
import sys
import time

from scripts.config import TestConfig # Added import

TEST_SERVER_PORT = 5001 # Define a specific port for the test server

from scripts.extensions import db # Added import

import argparse

def run_app():
    # Add the -playwright flag
    sys.argv.append('-playwright')
    app = create_app(config_class=TestConfig) # Modified to use TestConfig
    with app.app_context(): # Added app context
        db.create_all() # Create tables for the server process
    app.run(debug=False, host='0.0.0.0', port=TEST_SERVER_PORT, use_reloader=False) # Use TEST_SERVER_PORT

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run unit and end-to-end tests for WindFlag.')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                        help='Show this help message and exit.')
    args = parser.parse_args()

    server_process = multiprocessing.Process(target=run_app)
    server_process.start()

    # Give the server a moment to start
    time.sleep(10) # Increased sleep time

    # Run pytest
    exit_code = pytest.main(['--base-url', f'http://127.0.0.1:{TEST_SERVER_PORT}']) # Use TEST_SERVER_PORT in base-url

    # Shutdown the server
    server_process.terminate()
    server_process.join()

    # Exit with the same code as pytest
    exit(exit_code)
