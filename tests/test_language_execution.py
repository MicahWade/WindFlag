import unittest
from scripts.code_execution import execute_code_in_sandbox, CodeExecutionResult
import os

class TestLanguageExecution(unittest.TestCase):

    def test_python3_execution(self):
        code = "print('Hello, Python!')"
        expected_output = "Hello, Python!"
        result = execute_code_in_sandbox('python3', code, expected_output)
        self.assertTrue(result.success, f"Python execution failed: {result.error_message}")
        self.assertEqual(result.stdout, expected_output)

    def test_nodejs_execution(self):
        if not os.path.exists('/usr/bin/node'):
             print("Node.js executable not found, skipping Node.js test.")
             return

        code = "console.log('Hello, Node.js!');"
        expected_output = "Hello, Node.js!"
        result = execute_code_in_sandbox('nodejs', code, expected_output)
        self.assertTrue(result.success, f"Node.js execution failed: {result.error_message}")
        self.assertEqual(result.stdout, expected_output)

    def test_php_execution(self):
        if not os.path.exists('/home/linuxbrew/.linuxbrew/bin/php'):
             print("PHP executable not found, skipping PHP test.")
             return

        code = "<?php echo 'Hello, PHP!'; ?>"
        expected_output = "Hello, PHP!"
        result = execute_code_in_sandbox('php', code, expected_output)
        self.assertTrue(result.success, f"PHP execution failed: {result.error_message}")
        self.assertEqual(result.stdout, expected_output)

    def test_bash_execution(self):
        code = "echo 'Hello, Bash!'"
        expected_output = "Hello, Bash!"
        result = execute_code_in_sandbox('bash', code, expected_output)
        self.assertTrue(result.success, f"Bash execution failed: {result.error_message}")
        self.assertEqual(result.stdout, expected_output)

    def test_dart_execution(self):
        # Check if Dart is installed/configured before running
        if not os.path.exists('/opt/dart-sdk/bin/dart'): 
             print("Dart SDK not found, skipping Dart test.")
             return

        code = "void main() { print('Hello, Dart!'); }"
        expected_output = "Hello, Dart!"
        result = execute_code_in_sandbox('dart', code, expected_output)
        self.assertTrue(result.success, f"Dart execution failed: {result.error_message}")
        self.assertEqual(result.stdout, expected_output)
    
    def test_python3_input(self):
        code = "print(f'Input was: {input().strip()}')"
        expected_output = "Input was: test input"
        result = execute_code_in_sandbox('python3', code, expected_output, test_case_input="test input")
        self.assertTrue(result.success, f"Python input test failed: {result.error_message}")
        self.assertEqual(result.stdout, expected_output)

    def test_python3_setup_code(self):
        # Setup script creates a file, user code reads it.
        code = "with open('/sandbox/setup_data.txt', 'r') as f: print(f.read().strip())"
        expected_output = "HelloFromSetup"
        setup_code = "echo 'HelloFromSetup' > /sandbox/setup_data.txt"
        result = execute_code_in_sandbox('python3', code, expected_output, setup_code=setup_code)
        self.assertTrue(result.success, f"Python setup code test failed: {result.error_message}")
        self.assertEqual(result.stdout, expected_output)

if __name__ == '__main__':
    unittest.main()
