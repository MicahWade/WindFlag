import pytest
import multiprocessing
from app import create_app
import sys
import time

def run_app():
    # Add the -playwright flag
    sys.argv.append('-playwright')
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == '__main__':
    server_process = multiprocessing.Process(target=run_app)
    server_process.start()

    # Give the server a moment to start
    time.sleep(5)

    # Run pytest
    exit_code = pytest.main(['--base-url', 'http://127.0.0.1:5000'])

    # Shutdown the server
    server_process.terminate()
    server_process.join()

    # Exit with the same code as pytest
    exit(exit_code)
