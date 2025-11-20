# YAML Challenge Import

This document describes the YAML format for defining challenges and how to import them into the WindFlag CTF platform.

## YAML File Format

The YAML file should contain a top-level key `challenges`, which is a list of challenge objects. Each challenge object must have the following keys:

*   **`name`** (string, required): The unique name of the challenge.
*   **`description`** (string, required): A detailed description of the challenge, supporting markdown.
*   **`points`** (integer, required): The points awarded for solving the challenge.
*   **`category`** (string, optional): The name of the category the challenge belongs to. If the category does not exist, it will be created. Defaults to "Uncategorized".
*   **`case_sensitive`** (boolean, optional): Whether the flag submission is case-sensitive. Defaults to `true`.
*   **`multi_flag_type`** (string, optional): Defines how multiple flags are handled for the challenge.
    *   `SINGLE` (default): Only one flag needs to be submitted to solve the challenge.
    *   `ANY`: Any one of the defined flags solves the challenge.
    *   `ALL`: All defined flags must be submitted to solve the challenge.
    *   `N_OF_M`: A specific number (`multi_flag_threshold`) of flags must be submitted.
*   **`multi_flag_threshold`** (integer, optional): Required if `multi_flag_type` is `N_OF_M`. Specifies the number of flags (N) required to solve the challenge.
*   **`flags`** (list of strings, required): A list of all correct flag strings for the challenge.
*   **`hint_cost`** (integer, optional): The default points deducted from a user's score when they reveal a hint for this challenge. This applies if individual hints don't specify their own cost. Defaults to `0`.
*   **`hints`** (list of objects, optional): A list of hint objects for the challenge. Each hint object must have:
    *   **`title`** (string, required): The title of the hint, visible before revelation.
    *   **`content`** (string, required): The actual hint text, revealed upon purchase.
    *   **`cost`** (integer, optional): The specific cost of this hint. If not provided, the `challenge.hint_cost` will be used. Defaults to `0`.

### Example YAML

```yaml
challenges:
  - name: "Warmup Challenge"
    description: "This is a simple warmup challenge. Find the flag!"
    points: 50
    hint_cost: 10 # Default hint cost for this challenge
    category: "General Skills"
    case_sensitive: true
    multi_flag_type: SINGLE
    flags:
      - "flag{welcome_to_windflag}"
    hints:
      - title: "First Clue"
        content: "The flag format is flag{...}"
        cost: 5 # Override default hint_cost for this specific hint
      - title: "Second Clue"
        content: "Look for a hidden message in the source code."

  - name: "Multi-Flag Web"
    description: "Solve multiple parts of this web challenge."
    points: 150
    category: "Web Exploitation"
    case_sensitive: false
    multi_flag_type: ALL
    flags:
      - "flag{part_one_solved}"
      - "flag{part_two_complete}"
      - "flag{final_piece_found}"
    hints:
      - title: "Web Hint 1"
        content: "Check the network requests."
      - title: "Web Hint 2"
        content: "There's a hidden endpoint."

  - name: "N-of-M Crypto"
    description: "You need to find 2 out of 3 flags to solve this crypto puzzle."
    points: 200
    category: "Cryptography"
    multi_flag_type: N_OF_M
    multi_flag_threshold: 2
    flags:
      - "flag{crypto_key_a}"
      - "flag{crypto_key_b}"
      - "flag{crypto_key_c}"
    hints:
      - title: "Crypto Hint"
        content: "The algorithm is AES-256."
        cost: 25
```

## How to Import Challenges

To import challenges from a YAML file, use the `-yaml` or `-y` command-line argument when running `app.py`, followed by the path to your YAML file:

```bash
python app.py -yaml path/to/your/challenges.yaml
# or
python app.py -y path/to/your/challenges.yaml
```

**Important Notes:**
*   If a challenge with the same `name` already exists in the database, it will be skipped.
*   Categories will be created automatically if they do not exist.
*   Ensure your YAML file is correctly formatted to avoid parsing errors.

## Importing Users from JSON

You can import user accounts from a JSON file using the `-users` or `-u` command-line argument.

### JSON File Format

The JSON file should contain a list of user objects. Each user object must have at least `username` and `password` keys.

*   **`username`** (string, required): The unique username for the user.
*   **`password`** (string, required): The plain-text password for the user. This will be hashed upon import.
*   **`email`** (string, optional): The user's email address.
*   **`is_admin`** (boolean, optional): Set to `true` if the user should be an administrator. Defaults to `false`.
*   **`is_super_admin`** (boolean, optional): Set to `true` if the user should be a super administrator. Defaults to `false`.
*   **`hidden`** (boolean, optional): Set to `true` if the user should be hidden from the scoreboard. Defaults to `false`.

### Example JSON

```json
[
  {
    "username": "newuser1",
    "email": "newuser1@example.com",
    "password": "password123",
    "is_admin": false,
    "is_super_admin": false,
    "hidden": false
  },
  {
    "username": "admin_json",
    "email": "admin_json@example.com",
    "password": "adminpassword",
    "is_admin": true,
    "is_super_admin": false,
    "hidden": true
  },
  {
    "username": "superadmin_json",
    "email": "superadmin_json@example.com",
    "password": "superadminpassword",
    "is_admin": true,
    "is_super_admin": true,
    "hidden": true
  }
]
```

### How to Import Users

To import users from a JSON file, use the `-users` or `-u` command-line argument when running `app.py`, followed by the path to your JSON file:

```bash
python app.py -users path/to/your/users.json
# or
python app.py -u path/to/your/users.json
```

**Important Notes:**
*   If a user with the same `username` already exists in the database, they will be skipped.
*   Ensure your JSON file is correctly formatted to avoid parsing errors.

## Exporting Data to YAML

You can export various types of data from the database to a YAML file using the `-export-yaml` or `-e` command-line argument.

### Usage

```bash
python app.py -export-yaml <output_file_path> [data_type]
# or
python app.py -e <output_file_path> [data_type]
```

*   `<output_file_path>`: The path to the YAML file where the data will be saved.
*   `[data_type]`: (Optional) Specifies the type of data to export. If omitted, `all` data types will be exported.
    *   `all`: Exports users, categories, challenges, submissions, flag_attempts, and awards.
    *   `users`: Exports user data (username, email, admin status, hidden status, score).
    *   `categories`: Exports category data (name).
    *   `challenges`: Exports challenge data (name, description, points, category, case sensitivity, multi-flag type, threshold, flags).
    *   `submissions`: Exports submission data (solver username, challenge name, timestamp, score at submission).
    *   `flag_attempts`: Exports flag attempt data (user username, challenge name, submitted flag, correctness, timestamp).
    *   `awards`: Exports award data (recipient username, category name, points awarded, giver username, timestamp).

### Examples

Export all data to `all_data.yaml`:
```bash
python app.py -export-yaml all_data.yaml
```

Export only challenges to `challenges_export.yaml`:
```bash
python app.py -export-yaml challenges_export.yaml challenges
```

Export user data to `users.yaml`:
```bash
python app.py -e users.yaml users
```

**Important Notes:**
*   Password hashes are not exported for security reasons.
*   Timestamps are exported in ISO format.
