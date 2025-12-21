# WindFlag

A lightweight, self-hostable CTF platform featuring dynamic scoring, real-time analytics, and an integrated coding environment.

## Quick Start (Ubuntu)

For other operating systems (Arch, macOS, Windows) or advanced setups (PostgreSQL, Redis), see the [Installation Guide](docs/INSTALL.md).

### 1. Install Dependencies
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv bubblewrap
```

### 2. Setup Application
```bash
git clone https://github.com/MicahWade/WindFlag.git
cd WindFlag

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
./download_assets.sh
cp .env.template .env  # Edit .env to configure SECRET_KEY and other settings
```

### 3. Run
```bash
python app.py
# Access at http://127.0.0.1:5000/
```

To create an admin user immediately:
```bash
python app.py -admin <username> <password>
```

## Key Features

*   **CTF Core**: Jeopardy-style challenges, dynamic scoring, categories, and real-time scoreboard.
*   **Flag Types**: Single, Multiple (Any/All), N-of-M, and Regex/Dynamic support.
*   **File Downloads**: Admins can attach files to challenges for users to download.
*   **Code Execution**: Integrated editor and secure sandbox (Bubblewrap) for Python, Bash, Node.js, etc., supporting multiple test cases.
*   **Analytics**: Detailed charts for user progress, submission stats, and challenge difficulty.
*   **Import/Export**: Manage challenges via YAML or API. [See YAML Docs](docs/yaml.md).
*   **Themes**: Modern UI with multiple built-in themes (Cyberdeck, Retro, Dark, etc.).

## Documentation

*   **[Installation & Config](docs/INSTALL.md)**: Detailed setup, Redis, PostgreSQL, and Sandbox details.
*   **[Environment Variables](docs/ENV.md)**: Full list of configuration options in `.env`.
*   **[Administration](docs/admin.md)**: Managing users, awards, and hidden challenges.
*   **[Challenge Import](docs/yaml.md)**: YAML format specification and recipes.
*   **[API Docs](docs/API/api_overview.md)**: API endpoints for automation.

## Project Structure

*   `app.py`: Main entry point.
*   `config.py`: Configuration loader.
*   `scripts/`: Backend logic, routes, and models.
*   `templates/` & `static/`: Frontend assets (Jinja2, CSS, JS).
*   `tests/`: Unit and integration tests (`python app.py -run-tests`).

## Contributing

Contributions are welcome! Please open an issue for bugs or feature requests.
1. Fork & Clone.
2. Create a branch (`feature/my-feature`).
3. Submit a Pull Request.

**Testing:** Run `python app.py -run-tests` before submitting.