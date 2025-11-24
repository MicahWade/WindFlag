import re # Added for regex matching in static analysis
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

# Max output size for stdout/stderr
MAX_OUTPUT_SIZE_BYTES = 10 * 1024 # 10 KB

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

# Language-specific blacklists for static code analysis
# These are patterns or keywords that indicate potentially dangerous operations
LANGUAGE_BLACKLISTS = {
    'python3': {
        'forbidden_imports': [
            'os', 'subprocess', 'sys', 'socket', 'shutil', 'fcntl', 'resource',
            'ctypes', 'gc', 'mmap', 'multiprocessing', 'threading', 'signal',
            'urllib', 'requests', 'pathlib', 'glob', 'zipfile', 'tarfile', 'sqlite3',
            'pickle', 'marshal', 'http', 'ftplib', 'smtplib', 'poplib', 'imaplib',
            'xml', 'csv', 'json', 'yaml', 'configparser', 'logging', 'argparse',
            'getpass', 'pwd', 'grp', 'spwd', 'crypt', 'hashlib', 'hmac', 'ssl',
            'paramiko', 'fabric', 'pexpect', 'select', 'selectors'
        ],
        'forbidden_keywords': [
            'eval(', 'exec(', 'open(', 'compile(', '__import__', 'getattr(',
            'setattr(', 'delattr(', 'breakpoint(', 'input(', 'exit(', 'quit(',
            'system(', 'popen(', 'chmod(', 'chown(', 'rmdir(', 'removedirs(',
            'mkdir(', 'makedirs(', 'rename(', 'replace(', 'link(', 'symlink(',
            'walk(', 'fork(', 'kill(', 'alarm(', 'pause(', 'getuid(', 'setuid(',
            'geteuid(', 'seteuid(', 'getgid(', 'setgid(', 'getegid(', 'setegid(',
            'getgroups(', 'setgroups(', 'getresuid(', 'setresuid(', 'getresgid(',
            'setresgid(', 'umask(', 'getpgrp(', 'setpgrp(', 'getsid(', 'setsid(',
            'getpid(', 'getppid(', 'getpgid(', 'setpgid(', 'getsid(', 'setsid(',
            'nice(', 'sched_yield(', 'sched_getaffinity(', 'sched_setaffinity(',
            'sched_getparam(', 'sched_setparam(', 'sched_getscheduler(', 'sched_setscheduler(',
            'sched_rr_get_interval(', 'sched_getcpu(', 'lockf(', 'flock(', 'memlock(', 'memunlock(',
            'mmap(', 'munmap(', 'madvise(', 'mlock(', 'munlock(', 'msync(', 'getpriority(', 'setpriority(',
            'sched_get_priority_min(', 'sched_get_priority_max(', 'acct(', 'adjtime(', 'chroot(', 'fchdir(',
            'fchmod(', 'fchown(', 'fdatasync(', 'fgetxattr(', 'flistxattr(', 'fremovexattr(', 'fsetxattr(',
            'fsync(', 'getxattr(', 'listxattr(', 'removexattr(', 'setxattr(', 'lgetxattr(', 'llistxattr(',
            'lremovexattr(', 'lsetxattr(', 'sendfile(', 'statvfs(', 'fstatvfs(', 'sync()', 'syscall(',
            'socket.socket', 'socket.bind', 'socket.listen', 'socket.connect', 'socket.send', 'socket.recv',
            'http.client', 'urllib.request', 'requests.get', 'requests.post',
        ],
        'forbidden_regex': [
            r'import\s+[a-zA-Z_][a-zA-Z0-9_]*', # Catches general imports
            r'from\s+[a-zA-Z_][a-zA-Z0-9_]*\s+import', # Catches from ... import
            r'__builtins__\s*\[', # Accessing builtins directly
            r'subprocess\.run', r'os\.system', r'os\.popen', r'shutil\.', # Common dangerous calls
            r'while\s*True\s*:', # Catch infinite Python loops
        ]
    },
    'nodejs': {
        'forbidden_imports': [
            'child_process', 'fs', 'net', 'http', 'https', 'tls', 'dgram', 'dns',
            'os', 'path', 'url', 'process', 'crypto', 'vm', 'cluster', 'worker_threads'
        ],
        'forbidden_keywords': [
            'eval(', 'require(', 'import(', 'spawn(', 'exec(', 'fork(', 'system(',
            'setTimeout(', 'setInterval(', 'setImmediate(', 'process.exit(', 'console.log(' # Limit logging potentially
        ],
        'forbidden_regex': [
            r'require\s*\([\'"].*[\'"]\)',
            r'import\s+[\'"].*[\'"]',
            r'process\.stdout', r'process\.stderr',
            r'fs\.[a-zA-Z]+Sync', # Catches synchronous file system operations
            r'new\s+Function\s*\(' # Dynamic code execution
        ]
    },
    'php': {
        'forbidden_imports': [], # PHP doesn't have explicit "imports" in the same way
        'forbidden_keywords': [
            'exec(', 'shell_exec(', 'system(', 'passthru(', 'proc_open(', 'popen(',
            'eval(', 'assert(', 'include(', 'require(', 'file_get_contents(',
            'file_put_contents(', 'unlink(', 'rmdir(', 'mkdir(', 'chmod(',
            'chown(', 'chgrp(', 'symlink(', 'readfile(', 'fopen(', 'fsockopen(',
            'socket_create(', 'stream_socket_client(', 'curl_exec(',
            'phpinfo(', 'die(', 'exit(',
        ],
        'forbidden_regex': [
            r'include\s+[\'"].*[\'"]',
            r'require\s+[\'"].*[\'"]',
            r'\$\_GET', r'\$\_POST', r'\$\_REQUEST', r'\$\_FILES', r'\$\_SERVER', # Prevent external input
            r'new\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(\s*[\'"]ReflectionClass[\'"]', # Reflection attacks
        ]
    },
    'bash': {
        'forbidden_imports': [],
        'forbidden_keywords': [
            'rm ', 'sudo ', 'chown ', 'chmod ', 'ssh ', 'scp ', 'wget ', 'curl ',
            'nc ', 'netcat ', 'nmap ', 'apt-get ', 'yum ', 'dnf ', 'pacman ',
            'ifconfig ', 'ip addr ', 'route ', 'mount ', 'umount ', 'crontab ',
            'service ', 'systemctl ', 'kill ', 'pkill ', 'halt ', 'reboot ',
            'shutdown ', 'dd ', 'mkfs ', 'fdisk ', 'parted ', 'useradd ', 'userdel ',
            'groupadd ', 'groupdel ', 'passwd ', 'visudo ',
            'echo .* > ', 'echo .* >> ', # Redirects that write to files
            '> ', '>> ',
            '/', './', # Any path traversal or local execution attempt
        ],
        'forbidden_regex': [
            r'`.*`', # Command substitution
            r'\$\(.*\)', # Command substitution
            r'&&\s*', r'\|\|\s*', r';\s*', # Command chaining
            r'\bcat\s+/etc/passwd\b', # Specific file access
            r'\bcat\s+/etc/shadow\b',
            r'\bcat\s+/proc/self/cmdline\b',
            r'\/\w+\/\w+', # Absolute paths
        ]
    },
    'dart': {
        'forbidden_imports': [
            'dart:io', 'dart:cli', 'dart:developer', 'dart:ffi', 'dart:isolate',
            'package:http', 'package:path', 'package:shelf'
        ],
        'forbidden_keywords': [
            'Process.run(', 'Process.start(', 'File(', 'Directory(', 'Socket(', 'HttpServer(',
            'RawSocket(', 'Link(', 'Platform.environment', 'exit(',
        ],
        'forbidden_regex': [
            r'import\s+[\'"]dart:io[\'"]',
            r'import\s+[\'"]package:.*[\'"]',
            r'new\s+File\s*\('
        ]
    },
    'haskell': {
        'forbidden_imports': [
            'System.IO', 'System.Process', 'Network.Socket', 'System.Directory',
            'System.FilePath', 'GHC.IO', 'Control.Concurrent', 'Foreign.C', 'Foreign.Ptr'
        ],
        'forbidden_keywords': [
            'unsafePerformIO', 'System.cmd', 'System.rawSystem', 'System.process',
            'openFile', 'readFile', 'writeFile', 'appendFile', 'removeFile',
            'getContents', 'interact', 'hPutStrLn', 'hGetContents', 'exitWith',
            'socket', 'bind', 'listen', 'connect', 'send', 'recv', 'forkIO',
            'System.getEnv', 'System.setEnv', 'System.getArgs'
        ],
        'forbidden_regex': [
            r'import\s+System\.',
            r'import\s+Network\.',
            r'import\s+Foreign\.',
            r'import\s+GHC\.',
        ]
    }
}

def _static_code_analysis(language, code):
    """
    Performs static analysis on the submitted code to check for blacklisted patterns.
    Returns (True, "OK") if safe, or (False, "Error Message") if unsafe.
    """
    if language not in LANGUAGE_BLACKLISTS:
        return True, "OK" # No specific blacklist for this language, proceed with caution.

    blacklist = LANGUAGE_BLACKLISTS[language]

    # Check for forbidden imports
    for forbidden_import in blacklist.get('forbidden_imports', []):
        if forbidden_import in code:
            return False, f"Forbidden import '{forbidden_import}' detected in code. This is not allowed for security reasons."
        
    # Check for forbidden keywords (exact string match)
    for forbidden_keyword in blacklist.get('forbidden_keywords', []):
        if forbidden_keyword in code:
            return False, f"Forbidden keyword '{forbidden_keyword}' detected in code. This operation is not allowed."

    # Check for forbidden regex patterns
    for forbidden_regex_pattern in blacklist.get('forbidden_regex', []):
        if re.search(forbidden_regex_pattern, code, re.IGNORECASE | re.DOTALL): # Case-insensitive and dotall for multiline
            return False, f"Forbidden code pattern '{forbidden_regex_pattern}' detected. This operation is not allowed."
            
    return True, "OK"

class CodeExecutionResult:
    def __init__(self, success, stdout, stderr, error_message, is_timeout=False):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.error_message = error_message
        self.is_timeout = is_timeout

def execute_code_in_sandbox(language, code, expected_output, setup_code=None, test_case_input=None):
    """
    Executes user-provided code in a bwrap sandbox and compares its output.

    Args:
        language (str): The programming language (e.g., 'python3', 'nodejs').
        code (str): The user's submitted code.
        expected_output (str): The expected STDOUT from the code.
        setup_code (str, optional): Code/commands to run before user's code.
        test_case_input (str, optional): Input to be fed to the user's code via stdin.
        # timeout (int, optional): Maximum execution time in seconds. Removed as it's now fixed.

    Returns:
        CodeExecutionResult: An object containing success status, stdout, stderr, and error message.
    """
    CODE_SIZE_LIMIT_BYTES = 200 * 1024 # 0.2 MB
    EXECUTION_TIMEOUT_SECONDS = 5 # Fixed timeout

    if language not in LANGUAGE_CONFIGS:
        return CodeExecutionResult(False, "", "", f"Unsupported language: {language}")

    # Perform static code analysis before even writing to file or sandboxing
    is_safe, static_analysis_message = _static_code_analysis(language, code)
    if not is_safe:
        return CodeExecutionResult(False, "", "", f"Security check failed: {static_analysis_message}")

    if len(code.encode('utf-8')) > CODE_SIZE_LIMIT_BYTES:
        return CodeExecutionResult(False, "", "", f"Submitted code exceeds the size limit of {CODE_SIZE_LIMIT_BYTES / 1024} KB.")

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
                timeout=EXECUTION_TIMEOUT_SECONDS + 2, # Give bwrap itself a bit more time to clean up
                check=False # Don't raise an exception for non-zero exit codes
            )
            stdout = process.stdout.strip()
            stderr = process.stderr.strip()

            # Truncate output if it exceeds the limit
            if len(stdout) > MAX_OUTPUT_SIZE_BYTES:
                stdout = stdout[:MAX_OUTPUT_SIZE_BYTES] + f"\n... (output truncated to {MAX_OUTPUT_SIZE_BYTES} bytes)"
            if len(stderr) > MAX_OUTPUT_SIZE_BYTES:
                stderr = stderr[:MAX_OUTPUT_SIZE_BYTES] + f"\n... (output truncated to {MAX_OUTPUT_SIZE_BYTES} bytes)"


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

    print("\n--- Python Malicious Code Test (Server-Side) ---")
    python_malicious_code = "import os; print(os.listdir('/'))"
    python_malicious_result = execute_code_in_sandbox('python3', python_malicious_code, "Expected", timeout=5)
    print(f"Success: {python_malicious_result.success}, Error: '{python_malicious_result.error_message}'") # Should be False with a security error

    print("\n--- Python Infinite Loop Malicious Code Test (Server-Side) ---")
    python_infinite_loop_code = "while True:\n\tprint('i')"
    python_infinite_loop_result = execute_code_in_sandbox('python3', python_infinite_loop_code, "Expected", timeout=5)
    print(f"Success: {python_infinite_loop_result.success}, Error: '{python_infinite_loop_result.error_message}'") # Should be False with a security error

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
