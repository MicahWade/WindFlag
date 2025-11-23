import subprocess
import tempfile
import os
import secrets
import shutil

# Configuration for bwrap paths and language runtimes
# These should ideally be configurable or checked for existence
BWRAP_PATH = '/usr/bin/bwrap'
BWRAP_COMMON_ARGS = [
    '--unshare-all',
    '--die-with-parent',
    '--proc', '/proc',
    '--dev', '/dev',
    '--tmpfs', '/tmp',
    '--dir', '/sandbox', # A dedicated directory inside the sandbox
    '--setenv', 'PATH', '/usr/bin:/bin:/usr/local/bin' # Minimal PATH
    # Removed --rlimit-as, --rlimit-cpu, --rlimit-fsize as they are not supported by some bwrap versions.
    # Proper resource limiting should be handled via cgroups or a bwrap version that supports these flags.
]

# Language-specific configurations
# Tuple: (runtime_path, file_extension, execute_command_template, bind_args)
LANGUAGE_CONFIGS = {
    'python3': (
        '/usr/bin/python3', '.py',
        'python3 /sandbox/user_code.py',
        [
            ('/usr/bin/python3', '/usr/bin/python3'),
            # Relying on broader /usr/lib and /lib binds for Python libraries
            # Specific Python version paths are too brittle across systems
        ]
    ),
    'nodejs': (
        '/usr/bin/node', '.js',
        'node /sandbox/user_code.js',
        [
            ('/usr/bin/node', '/usr/bin/node'),
            # Consider adding /usr/lib/nodejs if it exists on the system, for global npm modules
        ]
    ),
    'php': (
        '/usr/bin/php', '.php',
        'php /sandbox/user_code.php',
        [
            ('/usr/bin/php', '/usr/bin/php'),
            ('/etc/php/', '/etc/php/'), # PHP needs its config
        ]
    ),
    'bash': (
        '/usr/bin/bash', '.sh',
        'bash /sandbox/user_code.sh',
        [
            ('/usr/bin/bash', '/usr/bin/bash'),
        ]
    ),
    'dart': (
        '/opt/dart-sdk/bin/dart', '.dart', # Actual executable path on host
        '/sandbox/dart-sdk/bin/dart run /sandbox/user_code.dart', # Command to execute inside sandbox
        [
            ('/opt/dart-sdk', '/sandbox/dart-sdk'), # Bind entire SDK into sandbox
        ]
    ),
    'haskell': (
        '/usr/bin/runghc', '.hs',
        'runghc /sandbox/user_code.hs',
        [
            ('/usr/bin/runghc', '/usr/bin/runghc'),
            ('/usr/bin/ghc', '/usr/bin/ghc'), # runghc might implicitly need ghc
            ('/usr/lib/ghc', '/usr/lib/ghc'), # Common GHC library path, typically /usr/lib/ghc
        ]
    )
}

class CodeExecutionResult:
    def __init__(self, success, stdout, stderr, error_message, is_timeout=False):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.error_message = error_message
        self.is_timeout = is_timeout

def execute_code_in_sandbox(language, code, expected_output, setup_code=None, test_case_input=None, timeout=10):
    """
    Executes user-provided code in a bwrap sandbox and compares its output.

    Args:
        language (str): The programming language (e.g., 'python3', 'nodejs').
        code (str): The user's submitted code.
        expected_output (str): The expected STDOUT from the code.
        setup_code (str, optional): Code/commands to run before user's code.
        test_case_input (str, optional): Input to be fed to the user's code via stdin.
        timeout (int, optional): Maximum execution time in seconds. Defaults to 10.

    Returns:
        CodeExecutionResult: An object containing success status, stdout, stderr, and error message.
    """
    if language not in LANGUAGE_CONFIGS:
        return CodeExecutionResult(False, "", "", f"Unsupported language: {language}")

    runtime_host_path, file_extension, execute_cmd_template, language_binds_config = LANGUAGE_CONFIGS[language]

    # Create temporary directory for user code and setup script
    temp_dir_name = f"sandbox_run_{secrets.token_urlsafe(8)}"
    temp_host_dir = os.path.join(tempfile.gettempdir(), temp_dir_name)
    os.makedirs(temp_host_dir, exist_ok=True)

    user_code_path_host = os.path.join(temp_host_dir, f"user_code{file_extension}")
    setup_code_path_host = None
    setup_cmd_in_sandbox = None

    try:
        # Write user code to a temporary file
        with open(user_code_path_host, 'w') as f:
            f.write(code)

        # Handle setup code if provided
        if setup_code:
            setup_code_path_host = os.path.join(temp_host_dir, "setup_script.sh")
            with open(setup_code_path_host, 'w') as f:
                f.write(setup_code)
            os.chmod(setup_code_path_host, 0o755) # Make executable
            setup_cmd_in_sandbox = "/sandbox/setup_script.sh"

        bwrap_args = [BWRAP_PATH] + BWRAP_COMMON_ARGS

        # Add common binds (e.g., /usr, /bin, /lib, /lib64, etc.)
        # Check if paths exist before binding
        for host_path, sandbox_path in [
            ('/usr', '/usr'),
            ('/bin', '/bin'),
            ('/lib', '/lib'),
            ('/lib64', '/lib64'),
            ('/etc/resolv.conf', '/etc/resolv.conf') # Allow DNS lookups
        ]:
            if os.path.exists(host_path):
                bwrap_args.extend(['--ro-bind', host_path, sandbox_path])
            else:
                print(f"Warning: Common bind path does not exist: {host_path}. Skipping.")
        
        # Add language-specific binds
        for host_path, sandbox_path in language_binds_config:
            if os.path.exists(host_path):
                bwrap_args.extend(['--ro-bind', host_path, sandbox_path])
            else:
                print(f"Warning: Language bind path does not exist: {host_path}. Skipping for {language}.")
        
        # Ensure the runtime executable itself is bound if not covered by a general /usr/bin bind
        if os.path.exists(runtime_host_path) and runtime_host_path not in [arg for sublist in language_binds_config for arg in sublist]:
             bwrap_args.extend(['--ro-bind', runtime_host_path, runtime_host_path])


        # Bind user's code and setup script into the sandbox
        bwrap_args.extend(['--ro-bind', user_code_path_host, f'/sandbox/user_code{file_extension}'])
        if setup_code_path_host:
            bwrap_args.extend(['--ro-bind', setup_code_path_host, '/sandbox/setup_script.sh'])

        # Command to execute inside the sandbox
        command_to_execute_in_sandbox = []
        if setup_cmd_in_sandbox:
            command_to_execute_in_sandbox = ['bash', '-c', f"{setup_cmd_in_sandbox} && {execute_cmd_template}"]
        else:
            command_to_execute_in_sandbox = execute_cmd_template.split()

        bwrap_cmd = bwrap_args + ['--'] + command_to_execute_in_sandbox # Use -- to separate bwrap args from inner command

        process_input = test_case_input if test_case_input else None # input should be string when text=True

        # Execute the bwrap command
        try:
            process = subprocess.run(
                bwrap_cmd,
                capture_output=True,
                text=True, # Decode stdout/stderr as text
                input=process_input,
                timeout=timeout + 2, # Give bwrap itself a bit more time to clean up
                check=False # Don't raise an exception for non-zero exit codes
            )
            stdout = process.stdout.strip()
            stderr = process.stderr.strip()

            if process.returncode != 0:
                error_message = f"Execution failed with exit code {process.returncode}."
                if stderr:
                    error_message += f"\nStderr: {stderr}"
                return CodeExecutionResult(False, stdout, stderr, error_message)

            if stdout == expected_output.strip():
                return CodeExecutionResult(True, stdout, stderr, "")
            else:
                return CodeExecutionResult(False, stdout, stderr, f"Output mismatch. Expected: '{expected_output.strip()}', Got: '{stdout}'")

        except subprocess.TimeoutExpired:
            # The process was terminated because it exceeded the timeout
            return CodeExecutionResult(False, "", "", "Execution timed out.", is_timeout=True)
        except FileNotFoundError:
            # bwrap itself or the runtime executable was not found
            return CodeExecutionResult(False, "", "", f"bwrap or runtime not found. Check paths: {BWRAP_PATH}, {runtime_host_path}")
        except Exception as e:
            # Catch other unexpected errors
            return CodeExecutionResult(False, "", "", f"An unexpected error occurred during execution: {e}")

    finally:
        # Clean up temporary directory on the host
        if os.path.exists(temp_host_dir):
            shutil.rmtree(temp_host_dir)

if __name__ == '__main__':
    print("--- Python Test ---")
    python_code = "print('Hello, Python!')"
    python_expected = "Hello, Python!"
    python_result = execute_code_in_sandbox('python3', python_code, python_expected, timeout=5)
    print(f"Success: {python_result.success}, Stdout: '{python_result.stdout}', Stderr: '{python_result.stderr}', Error: '{python_result.error_message}'")

    print("\n--- Python Incorrect Output Test ---")
    python_code_incorrect = "print('Wrong output')"
    python_result_incorrect = execute_code_in_sandbox('python3', python_code_incorrect, python_expected, timeout=5)
    print(f"Success: {python_result_incorrect.success}, Stdout: '{python_result_incorrect.stdout}', Stderr: '{python_result_incorrect.stderr}', Error: '{python_result_incorrect.error_message}'")

    print("\n--- Python Error Test ---")
    python_code_error = "raise Exception('Test Error')"
    python_result_error = execute_code_in_sandbox('python3', python_code_error, python_expected, timeout=5)
    print(f"Success: {python_result_error.success}, Stdout: '{python_result_error.stdout}', Stderr: '{python_result_error.stderr}', Error: '{python_result_error.error_message}'")

    print("\n--- Bash Test ---")
    bash_code = "echo 'Hello, Bash!'"
    bash_expected = "Hello, Bash!"
    bash_result = execute_code_in_sandbox('bash', bash_code, bash_expected, timeout=5)
    print(f"Success: {bash_result.success}, Stdout: '{bash_result.stdout}', Stderr: '{bash_result.stderr}', Error: '{bash_result.error_message}'")

    print("\n--- Node.js Test ---")
    nodejs_code = "console.log('Hello, Node.js!');"
    nodejs_expected = "Hello, Node.js!"
    nodejs_result = execute_code_in_sandbox('nodejs', nodejs_code, nodejs_expected, timeout=5)
    print(f"Success: {nodejs_result.success}, Stdout: '{nodejs_result.stdout}', Stderr: '{nodejs_result.stderr}', Error: '{nodejs_result.error_message}'")

    print("\n--- PHP Test ---")
    php_code = "<?php echo 'Hello, PHP!'; ?>"
    php_expected = "Hello, PHP!"
    php_result = execute_code_in_sandbox('php', php_code, php_expected, timeout=5)
    print(f"Success: {php_result.success}, Stdout: '{php_result.stdout}', Stderr: '{php_result.stderr}', Error: '{php_result.error_message}'")
    
    print("\n--- Dart Test ---")
    dart_code = "void main() { print('Hello, Dart!'); }"
    dart_expected = "Hello, Dart!"
    dart_result = execute_code_in_sandbox('dart', dart_code, dart_expected, timeout=5)
    print(f"Success: {dart_result.success}, Stdout: '{dart_result.stdout}', Stderr: '{dart_result.stderr}', Error: '{dart_result.error_message}'")

    print("\n--- Haskell Test ---")
    haskell_code = "main = putStrLn \"Hello, Haskell!\""
    haskell_expected = "Hello, Haskell!"
    haskell_result = execute_code_in_sandbox('haskell', haskell_code, haskell_expected, timeout=5)
    print(f"Success: {haskell_result.success}, Stdout: '{haskell_result.stdout}', Stderr: '{haskell_result.stderr}', Error: '{haskell_result.error_message}'")
    
    print("\n--- Python with Input Test ---")
    python_input_code = "import sys; print(f'Input was: {sys.stdin.read().strip()}')"
    python_input_expected = "Input was: test input"
    python_input_result = execute_code_in_sandbox('python3', python_input_code, python_input_expected, test_case_input="test input", timeout=5)
    print(f"Success: {python_input_result.success}, Stdout: '{python_input_result.stdout}', Stderr: '{python_input_result.stderr}', Error: '{python_input_result.error_message}'")

    print("\n--- Python with Simple Setup Code Test ---")
    # Setup script creates a file, user code reads it. This is more robust than env vars.
    python_setup_code = "with open('/sandbox/setup_data.txt', 'r') as f: print(f.read().strip())"
    python_setup_expected = "HelloFromSetup"
    python_setup_script = "echo 'HelloFromSetup' > /sandbox/setup_data.txt" # Create file in writable /sandbox
    python_setup_result = execute_code_in_sandbox('python3', python_setup_code, python_setup_expected, setup_code=python_setup_script, timeout=5)
    print(f"Success: {python_setup_result.success}, Stdout: '{python_setup_result.stdout}', Stderr: '{python_setup_result.stderr}', Error: '{python_setup_result.error_message}'")
