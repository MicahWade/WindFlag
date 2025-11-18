import pytest
import multiprocessing
from app import create_app
import sys
import time
import os # Import os for process management

from scripts.config import TestConfig # Added import

TEST_SERVER_PORT = 5001 # Define a specific port for the test server

from scripts.extensions import db # Added import

from scripts.seed import seed_database
import argparse

# Function to run the Flask app for testing (non-demo mode)
def run_app_for_testing():
    app = create_app(config_class=TestConfig)
    with app.app_context():
        db.create_all() # Create tables for the server process
    app.run(debug=False, host='0.0.0.0', port=TEST_SERVER_PORT, use_reloader=False) # Use TEST_SERVER_PORT

# Function to run the Flask app for demo mode
def run_app_for_demo(port, debug_mode):
    app = create_app(config_class=TestConfig)
    with app.app_context():
        db.create_all()
        seed_database() # Seed database for demo mode
    app.run(debug=debug_mode, host='0.0.0.0', port=port, use_reloader=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run unit and end-to-end tests for WindFlag.')
    parser.add_argument('-d', '--demo', action='store_true',
                        help='Run the server in demo mode with test data, without running tests.')
    parser.add_argument('-p', '--playwright', action='store_true',
                        help='Run only Playwright end-to-end tests.')
    parser.add_argument('-f', '--file', type=str,
                        help='Run a specific test file or directory (e.g., tests/unit/test_example.py).')
    parser.add_argument('-t', '--time', type=int,
                        help='Duration in seconds to run the demo server before shutting down automatically. Must be used with -d.')
    args = parser.parse_args()

    if args.time and not args.demo:
        parser.error("--time can only be used with --demo (-d).")

    if args.demo:
        print("Starting server in demo mode...")
        # Start the Flask app in a separate process for demo mode
        server_process = multiprocessing.Process(target=run_app_for_demo, args=(TEST_SERVER_PORT, True))
        server_process.start()
        
        if args.time:
            print(f"Demo server will shut down in {args.time} seconds.")
            time.sleep(args.time)
            server_process.terminate()
            server_process.join()
            print("Demo server shut down automatically.")
        else:
            print(f"Demo server running indefinitely on http://127.0.0.1:{TEST_SERVER_PORT}. Press Ctrl+C to stop.")
            # Keep the main process alive while the server_process runs
            server_process.join() # Wait for the server process to terminate (e.g., via Ctrl+C)

    else: # Non-demo mode (running tests)
        server_process = multiprocessing.Process(target=run_app_for_testing) # Use the dedicated function
        server_process.start()

        # Give the server a moment to start
        time.sleep(1) # Increased sleep time

        pytest_args = ['--base-url', f'http://127.0.0.1:{TEST_SERVER_PORT}']
        if args.file:
            pytest_args.append(args.file)
        elif args.playwright:
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