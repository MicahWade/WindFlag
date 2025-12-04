# Detailed Installation & Configuration Guide

This guide covers installation on various operating systems and advanced configuration options for WindFlag (Redis, PostgreSQL, Code Execution).

## 1. Install System Dependencies

### Python 3.8+ & pip
*   **Ubuntu/Debian:**
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip python3-venv
    ```
*   **Arch Linux:**
    ```bash
    sudo pacman -S python python-pip
    ```
*   **RedHat/Fedora:**
    ```bash
    sudo dnf install python3 python3-pip python3-venv
    ```
*   **macOS:**
    Install [Homebrew](https://brew.sh) and then `brew install python`.
*   **Windows:**
    Download from [python.org](https://www.python.org/downloads/). Check "Add Python to PATH".

## 2. Code Execution Sandbox (Optional)

WindFlag uses `bwrap` (Bubblewrap) for secure code execution.

*   **Ubuntu/Debian:** `sudo apt install bubblewrap`
    *   *Note for Ubuntu 23.10/24.04+:* See [ENV.md](ENV.md) for AppArmor configuration.
*   **Arch Linux:** `sudo pacman -S bubblewrap`
*   **RedHat/Fedora:** `sudo dnf install bubblewrap`
*   **macOS/Windows:** Not supported directly. Use Docker or a Linux VM.

**Language Runtimes:**
Install the languages you want to support (e.g., `nodejs`, `php`, `dart`). Run `python3 configure_runtimes.py` to auto-detect.

## 3. Advanced Database Setup (PostgreSQL)

For production, PostgreSQL is recommended over the default SQLite.

1.  **Install PostgreSQL** (e.g., `sudo apt install postgresql postgresql-contrib`).
2.  **Create DB & User:**
    ```sql
    CREATE DATABASE windflag_db;
    CREATE USER windflag_user WITH PASSWORD 'secure_password';
    GRANT ALL PRIVILEGES ON DATABASE windflag_db TO windflag_user;
    ```
3.  **Configure `.env`:**
    ```
    USE_POSTGRES=True
    DATABASE_URL=postgresql://windflag_user:secure_password@localhost:5432/windflag_db
    ```

## 4. Caching Setup (Redis)

To improve performance:

1.  **Install Redis** (e.g., `sudo apt install redis-server`).
2.  **Start Redis:** `sudo systemctl start redis-server`.
3.  **Configure `.env`:**
    ```
    ENABLE_REDIS_CACHE=True
    REDIS_URL=redis://localhost:6379/0
    ```
