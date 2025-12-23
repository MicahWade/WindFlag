# WindFlag

**WindFlag is a versatile and easy-to-deploy Capture The Flag (CTF) platform designed for competitive cybersecurity events, educational purposes, and skill development.** It combines powerful features with a simple setup, offering dynamic scoring, real-time analytics, and a secure, integrated coding environment.

---

## ✨ Features at a Glance

*   **Jeopardy-Style CTF**: Engage with classic challenge categories and a real-time scoreboard.
*   **Flexible Flag Management**: Supports various flag types including single, multiple (any/all), N-of-M, and dynamic regex-based flags.
*   **Integrated Code Execution**: A secure sandbox environment (via Bubblewrap) for coding challenges, supporting multiple languages like Python, Bash, and Node.js. Includes an in-browser editor and test case evaluation.
*   **Detailed Analytics**: Monitor user progress, submission trends, and challenge difficulty with insightful charts.
*   **Easy Challenge Import/Export**: Manage your CTF content effortlessly using YAML or dedicated API endpoints.
*   **Customizable Theming**: Modern, responsive UI with several built-in themes (Cyberdeck, Retro, Dark, etc.) to personalize your platform.
*   **Challenge Attachments**: Easily provide files for users to download directly from challenges.

## 🚀 Quick Start (Ubuntu/Debian)

Get your WindFlag instance up and running in minutes. For other operating systems (Arch, macOS, Windows) or advanced setups (PostgreSQL, Redis), please refer to the [Installation Guide](docs/INSTALL.md).

### 1. Install Dependencies
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv bubblewrap git
```

### 2. Setup Application
```bash
git clone https://github.com/MicahWade/WindFlag.git
cd WindFlag

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
./download_assets.sh
cp .env.template .env  # Customize .env for SECRET_KEY, database, and other settings
```

### 3. Run WindFlag
```bash
python app.py
# Access your CTF platform at http://127.0.0.1:5000/
```

**To create an administrator account on first run:**
```bash
python app.py -admin <username> <password>
```

## 📖 Documentation & Guides

*   **[Full Installation Guide](docs/INSTALL.md)**: Comprehensive setup instructions, including advanced configurations.
*   **[Environment Variables](docs/ENV.md)**: All available configuration options for your `.env` file.
*   **[Administration Guide](docs/admin.md)**: How to manage users, awards, categories, and hidden challenges.
*   **[Challenge YAML Format](docs/yaml.md)**: Details on creating and importing challenges using YAML.
*   **[API Overview](docs/API/api_overview.md)**: Explore API endpoints for platform automation and integration.

##🤝 Contributing

We welcome contributions! If you encounter a bug or have a feature idea, please open an issue.

1.  **Fork & Clone**: Get your own copy of the repository.
2.  **Create a Branch**: Use a descriptive name (e.g., `feature/add-dark-mode` or `fix/login-bug`).
3.  **Submit a Pull Request**: Detail your changes and improvements.