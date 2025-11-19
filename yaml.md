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

### Example YAML

```yaml
challenges:
  - name: "Warmup Challenge"
    description: "This is a simple warmup challenge. Find the flag!"
    points: 50
    category: "General Skills"
    case_sensitive: true
    multi_flag_type: SINGLE
    flags:
      - "flag{welcome_to_windflag}"

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
