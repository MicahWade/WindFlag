import os

THEMES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'themes')
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.py')

def scan_themes():
    """
    Scans the themes directory for valid themes.
    A valid theme is a subdirectory containing a theme.css file.
    Returns a list of theme names.
    """
    themes = []
    if not os.path.exists(THEMES_DIR):
        return themes

    for item in os.listdir(THEMES_DIR):
        theme_path = os.path.join(THEMES_DIR, item)
        if os.path.isdir(theme_path):
            css_file_path = os.path.join(theme_path, 'theme.css')
            if os.path.exists(css_file_path):
                themes.append(item)
    return sorted(themes)

def get_active_theme():
    """
    Retrieves the currently active theme from config.py.
    """
    try:
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                if line.startswith('ACTIVE_THEME ='):
                    return line.split('=')[1].strip().strip("'\"")
    except FileNotFoundError:
        pass # config.py might not exist yet or be malformed
    return 'default' # Default theme

def set_active_theme(theme_name):
    """
    Sets the active theme in config.py.
    """
    current_config_content = []
    found = False
    try:
        with open(CONFIG_FILE, 'r') as f:
            current_config_content = f.readlines()
        
        with open(CONFIG_FILE, 'w') as f:
            for line in current_config_content:
                if line.startswith('ACTIVE_THEME ='):
                    f.write(f"ACTIVE_THEME = '{theme_name}'\n")
                    found = True
                else:
                    f.write(line)
            if not found:
                f.write(f"\nACTIVE_THEME = '{theme_name}'\n") # Add if not found
    except FileNotFoundError:
        with open(CONFIG_FILE, 'w') as f:
            f.write(f"ACTIVE_THEME = '{theme_name}'\n")

if __name__ == '__main__':
    print("Available Themes:", scan_themes())
    print("Active Theme:", get_active_theme())
    # Example usage:
    # set_active_theme('dark')
    # print("New Active Theme:", get_active_theme())
