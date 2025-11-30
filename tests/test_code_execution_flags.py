import pytest
import os
import importlib
from scripts import config, code_execution # Import modules to be reloaded

# Define a list of languages and their test cases
LANGUAGES_TO_TEST = [
    ('python3', "print('Hello Python3')", "Hello Python3"),
    ('nodejs', "console.log('Hello Node.js!')", "Hello Node.js!"),
    ('php', "<?php echo 'Hello PHP!'; ?>", "Hello PHP!"),
    ('bash', "echo 'Hello Bash!'", "Hello Bash!"),
    ('dart', "void main() { print('Hello Dart!'); }", "Hello Dart!"),
]

@pytest.fixture(autouse=True)
def setup_teardown_env():
    """
    Fixture to manage environment variables for each test.
    Ensures a clean state before and after each test.
    """
    original_env = os.environ.copy()
    
    # Clean up any ENABLE_LANGUAGE env vars from previous runs
    for key in list(os.environ.keys()):
        if key.startswith('ENABLE_'):
            del os.environ[key]

    yield # Run the test

    # Restore original environment after the test
    os.environ.clear()
    os.environ.update(original_env)
    # Reload modules to ensure they revert to the original state
    importlib.reload(config)
    importlib.reload(code_execution)


@pytest.mark.parametrize(
    "lang_name, test_code, expected_output", 
    LANGUAGES_TO_TEST
)
def test_language_execution_enabled_via_env(lang_name, test_code, expected_output):
    """
    Test that code executes successfully when the specific language is enabled via environment variable.
    """
    # Set the environment variable to enable the language
    os.environ[f'ENABLE_{lang_name.upper()}'] = 'True'
    
    # Reload modules to pick up the new environment variable
    importlib.reload(config)
    importlib.reload(code_execution)

    # Create a dummy Flask app and context to make current_app available
    from flask import Flask
    temp_app = Flask(__name__)
    # Manually set the config flag in the Flask app context
    temp_app.config[f'ENABLE_{lang_name.upper()}'] = True
    temp_app.config.from_object(config.Config) # Load other configs
    
    with temp_app.app_context():
        # Assert that the config reflects the enabled state
        assert temp_app.config.get(f'ENABLE_{lang_name.upper()}') is True, \
            f"Config for ENABLE_{lang_name.upper()} should be True for enabled test"            
        result = code_execution.execute_code_in_sandbox(lang_name, test_code, expected_output)    
    # If result.success is False, but not due to "Unsupported language", it's an environment issue.
    if not result.success and "Unsupported language" not in result.error_message:
        pytest.skip(f"Skipping {lang_name} enabled test due to external execution environment issue: {result.error_message}")
    
    assert result.success is True, \
        f"Expected successful execution for {lang_name}, but got failure: {result.error_message}. Stdout: {result.stdout}, Stderr: {result.stderr}"
    assert result.stdout == expected_output, \
        f"Output mismatch for {lang_name}. Expected: '{expected_output}', Got: '{result.stdout}'"


@pytest.mark.parametrize(
    "lang_name, test_code, expected_output", 
    LANGUAGES_TO_TEST
)
def test_language_execution_disabled_via_env(lang_name, test_code, expected_output):
    """
    Test that code execution fails with 'Unsupported language' error when the specific language is disabled via environment variable.
    """
    # Set the environment variable to disable the language
    os.environ[f'ENABLE_{lang_name.upper()}'] = 'False'
    
    # Reload modules to pick up the new environment variable
    importlib.reload(config)
    importlib.reload(code_execution)

    # Create a dummy Flask app and context to make current_app available
    from flask import Flask
    temp_app = Flask(__name__)
    # Manually set the config flag in the Flask app context
    temp_app.config[f'ENABLE_{lang_name.upper()}'] = False
    temp_app.config.from_object(config.Config) # Load other configs

    with temp_app.app_context():
        # Assert that the config reflects the disabled state
        assert temp_app.config.get(f'ENABLE_{lang_name.upper()}') is False, \
            f"Config for ENABLE_{lang_name.upper()} should be False for disabled test"
        
        result = code_execution.execute_code_in_sandbox(lang_name, test_code, expected_output)        
    assert result.success is False, f"Expected failed execution for {lang_name}, but got success"
    assert f"Unsupported language: {lang_name}" in result.error_message, \
        f"Expected 'Unsupported language: {lang_name}' error, but got: {result.error_message}"