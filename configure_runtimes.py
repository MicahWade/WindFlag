import sys
import os
import re
import shutil

target_file = "scripts/code_execution.py"

def get_path(cmd):
    path = shutil.which(cmd)
    if path:
        # Resolve symlinks to get the real path
        return os.path.realpath(path)
    return None

def update_config(content, key, executable_path):
    if not executable_path:
        print(f"Warning: {key} runtime not found. Skipping update.")
        return content
    
    print(f"Updating {key} to {executable_path}")
    
    # Regex to match the tuple entry in LANGUAGE_CONFIGS
    # Matches: 'key': ( 'path',
    pattern = r"'" + re.escape(key) + r"': \(\s*'[^']+'"
    replacement = f"'{key}': (\n        '{executable_path}'"
    
    # We also need to update the command template which often repeats the path
    # But the current structure is inconsistent.
    # Let's stick to a simpler approach:
    # We will read the file and replace the specific hardcoded string if it matches known patterns?
    # No, that fails if the file has changed.
    
    # Better approach: Regex match the whole tuple structure specifically for each language
    # and reconstruct it using the new path.
    
    if key == 'nodejs':
        # Node usually needs its install dir bound
        install_dir = os.path.dirname(os.path.dirname(executable_path))
        # Construct the new config block
        new_config = f"'" + key + "': (\n        '" + executable_path + "', '.js',\n        '" + executable_path + " /sandbox/user_code.js',\n        [
            ('" + install_dir + "', '" + install_dir + "'),
        ]
    )"
        # Regex to match the existing block. This is tricky with multi-line.
        # We assume standard indentation.
        # Match from key start to the closing parenthesis of the tuple.
        # Note: This regex is somewhat brittle to formatting changes.
        regex = r"'" + re.escape(key) + r"': \(\s*'[^']+', '[^']+',\s*'[^']+',\s*\[\s*\('[^']+', '[^']+'\),\s*\]\s*\)"
        
        # Try to find it using DOTALL
        match = re.search(regex, content, re.DOTALL)
        if match:
            content = content.replace(match.group(0), new_config)
        else:
            print(f"Could not match existing config block for {key}. Trying simple path replacement.")
            # Fallback: Replace the path string wherever it occurs in the block
            # This is risky but might work if the file uses the same path in multiple places
            pass

    elif key == 'dart':
        # Dart needs sdk bind
        install_dir = os.path.dirname(os.path.dirname(executable_path))
        new_config = f"'" + key + "': (\n        '" + executable_path + "', '.dart', # Actual executable path on host\n        '/sandbox/dart-sdk/bin/dart run /sandbox/user_code.dart', # Command to execute inside sandbox\n        [
            ('" + install_dir + "', '/sandbox/dart-sdk'), # Bind entire SDK into sandbox\n        ]
    )"
        regex = r"'" + re.escape(key) + r"': \(\s*'[^']+', '[^']+',\s*.* # Actual executable path on host\s*'[^']+', # Command to execute inside sandbox\s*\[\s*\('[^']+', '[^']+'\), # Bind entire SDK into sandbox\s*\]\s*\)"
        
        match = re.search(regex, content, re.DOTALL)
        if match:
            content = content.replace(match.group(0), new_config)

    else:
        # For others (python3, php, bash), we generally just update the executable path
        # and the command template if it uses the full path.
        
        # Strategy: Find the lines starting with the key and replace the executable path.
        # 'python3': ( 
        #    '/path/to/python', ...
        regex_start = r"'" + re.escape(key) + r"': \(\s*'([^']+)'"
        match = re.search(regex_start, content)
        if match:
            old_path = match.group(1)
            # Replace occurrences of old_path with new_path ONLY within the LANGUAGE_CONFIGS block?
            # Or globally? Globally is probably safe for these specific full paths.
            content = content.replace(old_path, executable_path)
            
    return content

with open(target_file, 'r') as f:
    content = f.read()

# Update BWRAP_PATH
bwrap_path = get_path('bwrap')
if bwrap_path:
    print(f"Updating bwrap to {bwrap_path}")
    content = re.sub(r"BWRAP_PATH = '[^']+'", f"BWRAP_PATH = '{bwrap_path}'", content)
else:
    print("Warning: bwrap not found. Code execution will likely fail.")

# Update Languages
python_path = get_path('python3')
if python_path:
    content = update_config(content, 'python3', python_path)

node_path = get_path('node')
if node_path:
    content = update_config(content, 'nodejs', node_path)

php_path = get_path('php')
if php_path:
    content = update_config(content, 'php', php_path)

bash_path = get_path('bash')
if bash_path:
    content = update_config(content, 'bash', bash_path)

dart_path = get_path('dart')
if dart_path:
    content = update_config(content, 'dart', dart_path)

with open(target_file, 'w') as f:
    f.write(content)

print("Configuration update complete.")
