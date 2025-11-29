# YAML Challenge Import

This document describes the YAML format for defining challenges and how to import them into the WindFlag CTF platform.

## Category YAML File Format

The YAML file can optionally contain a top-level key `categories`, which is a list of category objects. If a category is not defined here but is referenced by a challenge, it will be created with default `NONE` unlock type.

Each category object can have the following keys:

*   **`name`** (string, required): The unique name of the category.
*   **`description`** (string, optional): A description of the category. This field is primarily for documentation within the YAML and helps administrators understand the category's purpose.
*   **`unlock_type`** (string, optional): The type of unlocking mechanism for the category. Defaults to `NONE`.
    *   `NONE`: The category is always visible and its challenges are accessible without any prerequisites. This is suitable for initial "warmup" categories or those that are always available.
    *   `PREREQUISITE_PERCENTAGE`: The category unlocks after a specified percentage of *all* available challenges across the platform (or within specified categories if `prerequisite_count_category_names` is used with `COMBINED`) have been solved by the user. This encourages broader engagement before advanced categories are revealed.
    *   `PREREQUISITE_COUNT`: The category unlocks after a specific number of challenges (from any category, or specified categories) have been solved. Similar to `PREREQUISITE_PERCENTAGE` but based on an absolute count.
    *   `PREREQUISITE_CHALLENGES`: The category unlocks only after a specific list of named challenges (`prerequisite_challenge_names`) have been solved by the user. This is useful for creating linear progression paths or requiring mastery of foundational challenges.
    *   `TIMED`: The category becomes available at a predefined future date and time (`unlock_date_time`). Useful for releasing challenges in phases or at specific event times.
    *   `COMBINED`: This advanced type allows for a combination of the above prerequisites. For example, a category might require solving a certain percentage of challenges *and* be timed to unlock after a specific date. When using `COMBINED`, ensure all relevant prerequisite fields (e.g., `prerequisite_percentage_value`, `prerequisite_count_value`, `unlock_date_time`) are correctly specified.
*   **`prerequisite_percentage_value`** (integer, optional): Required if `unlock_type` is `PREREQUISITE_PERCENTAGE` or `COMBINED`. An integer between 1 and 100 representing the percentage of challenges that must be solved. For example, `50` means 50% of challenges must be solved.
*   **`prerequisite_count_value`** (integer, optional): Required if `unlock_type` is `PREREEREQUISITE_COUNT` or `COMBINED`. The absolute number of challenges that must be solved. For example, `5` means 5 challenges must be solved.
*   **`prerequisite_count_category_names`** (list of strings, optional): Used with `PREREQUISITE_COUNT` or `COMBINED`. If provided, `prerequisite_count_value` will only consider challenges within these specified categories. If omitted, it applies to all challenges globally. This allows for fine-grained control over which challenges contribute to the prerequisite count.
*   **`prerequisite_challenge_names`** (list of strings, optional): Used with `PREREQUISITE_CHALLENGES` or `COMBINED`. A list of the exact `name` strings of challenges that must be solved before this category unlocks. All listed challenges must be solved.
*   **`unlock_date_time`** (string, optional): Required if `unlock_type` is `TIMED` or `COMBINED`. The UTC datetime string (e.g., "YYYY-MM-DDTHH:MM:SSZ") when the category unlocks. It's crucial to use UTC format to avoid timezone issues.
*   **`is_hidden`** (boolean, optional): If `true`, the category will be entirely hidden from non-admin users until its unlock conditions are met. If `false` (default), the category might be visible but its challenges inaccessible until unlocked. This is useful for surprise categories or those that should only appear once certain conditions are met.

### Example Category YAML

```yaml
categories:
  - name: "Warmup"
    description: "Easy challenges to get started with basic CTF skills."
    unlock_type: "NONE" # Always available
  - name: "Web Fundamentals"
    description: "Introduce common web vulnerabilities and exploitation techniques."
    unlock_type: "PREREQUISITE_COUNT"
    prerequisite_count_value: 3 # Requires 3 challenges from any category to be solved
  - name: "Advanced Reversing"
    description: "Deep dive into binary analysis and reverse engineering."
    unlock_type: "PREREQUISITE_CHALLENGES"
    prerequisite_challenge_names:
      - "Intro to Assembly"
      - "Basic Debugging" # Requires both "Intro to Assembly" and "Basic Debugging" to be solved
  - name: "Mid-Game Unlock"
    description: "A category that becomes available midway through the CTF event."
    unlock_type: "TIMED"
    unlock_date_time: "2025-12-25T12:00:00Z" # Unlocks on Dec 25, 2025, at 12:00 PM UTC
    is_hidden: true # Category is completely hidden until this time
  - name: "Final Boss"
    description: "The ultimate challenges, unlocked after significant progress."
    unlock_type: "COMBINED"
    prerequisite_percentage_value: 75 # Requires 75% of all challenges solved
    unlock_date_time: "2025-12-26T00:00:00Z" # Also unlocks at a specific time
```

## Challenge YAML File Format

The YAML file should contain a top-level key `challenges`, which is a list of challenge objects. Each challenge object must have the following keys:

*   **`name`** (string, required): The unique name of the challenge. This name is used for identification, prerequisites, and display on the scoreboard. It should be concise and descriptive.
*   **`description`** (string, required): A detailed explanation of the challenge, including the problem statement, context, and any necessary attachments or links. Supports markdown formatting for rich text, code blocks, images, and links.
*   **`points`** (integer, required): The initial points awarded for solving the challenge. This value can decrease over time if point decay is configured.
*   **`point_decay_type`** (string, optional): The strategy for how the challenge's point value decreases as more users solve it. Defaults to `STATIC`.
    *   `STATIC`: The challenge's points remain constant at its initial `points` value, regardless of how many users solve it or when they solve it. Simple and predictable.
    *   `LINEAR`: The challenge's points decrease linearly with each successive solve. The rate of this decrease is determined by `point_decay_rate`. This encourages early solves. For example, if `points` is 100, `point_decay_rate` is 5, points might go 100, 95, 90, etc.
    *   `LOGARITHMIC`: The challenge's points decrease logarithmically. This provides a gentler decay curve than linear, where the point reduction is significant initially but slows down over time. Still rewards early solves but avoids challenges becoming worth very little too quickly. The exact formula typically involves `log(number_of_solves + 1)`.
*   **`point_decay_rate`** (integer, optional): The rate of decay for `LINEAR` or `LOGARITHMIC` decay types. For `LINEAR`, this is the amount of points reduced per solve. For `LOGARITHMIC`, it influences the slope of the decay curve (a higher rate means faster decay). Not applicable for `STATIC` decay.
*   **`minimum_points`** (integer, optional): The lowest number of points a challenge can be worth due to decay. Defaults to `1`. This prevents challenges from becoming worthless.
*   **`proactive_decay`** (boolean, optional): If `true`, points for this challenge will decay for *all* users (including those who have already solved it) when a new user solves it. If `false` (default), decay only affects the point value for future solvers; previous solvers retain the points they earned at their solve time. `proactive_decay` should be used cautiously as it can alter past scores.
*   **`category`** (string, optional): The name of the category the challenge belongs to. If a category with this name does not exist, it will be automatically created (with `NONE` unlock type) upon import. Defaults to "Uncategorized".
*   `case_sensitive` (boolean, optional): Determines whether the flag submission must match the case of the defined `flags`. Defaults to `true` (e.g., "FLAG{example}" is different from "flag{example}"). Set to `false` for more lenient flag checking.
*   **`multi_flag_type`** (string, optional): Defines how multiple flags are handled for the challenge, offering flexibility for different challenge designs. **(Changed from `flag_type` for consistency)**
    *   `SINGLE` (default): This is the traditional CTF model. The challenge has exactly one correct flag. The first successful submission of this flag solves the challenge for the user.
    *   `ANY`: The challenge has multiple possible correct flags defined in the `flags` list. A user needs to submit *any one* of these flags correctly to solve the challenge. Useful for challenges with multiple valid solutions or varied outputs.
    *   `ALL`: The challenge requires a user to submit *all* defined flags correctly to solve the challenge. Each flag must be submitted individually, and the challenge is marked solved only after the last required flag is submitted. Ideal for multi-stage challenges or those requiring discovery of several hidden components.
    *   `N_OF_M`: An advanced flag type where a user must submit 'N' out of 'M' total defined flags (`flags` list) to solve the challenge. The value for 'N' is specified by `multi_flag_threshold`. This is excellent for challenges where partial solutions grant points, or where a set of options exist, and only a subset are required.
    *   `DYNAMIC`: The flag is not explicitly defined in the YAML. Instead, it is dynamically generated or validated by the application logic (e.g., via a custom script or API). This is for highly interactive or custom-logic challenges. Requires backend implementation beyond YAML definition.
    *   `HTTP`: The flag is retrieved from an external HTTP endpoint. The platform makes a request to a specified URL, and the response (or part of it) is treated as the flag. Useful for challenges involving external services or APIs. Requires additional configuration (e.g., the URL) not directly shown in this YAML.
*   **`multi_flag_threshold`** (integer, optional): Required if `multi_flag_type` is `N_OF_M`. Specifies the number of flags ('N') required to solve the challenge. For instance, if `flags` contains 5 items and `multi_flag_threshold` is `3`, a user must submit any 3 of those 5 flags.
*   **`flags`** (list of strings, optional): A list of all correct flag strings for the challenge. This field is *not* required for `DYNAMIC` or `HTTP` flag types, as their flags are managed externally. Each string in the list represents a valid flag.
*   **`challenge_type`** (string, optional): The type of challenge. Defaults to `FLAG`.
    *   `FLAG`: Traditional CTF challenge where a flag is submitted.
    *   `CODING`: A challenge where user-submitted code is executed and evaluated against expected output.
*   **`language`** (string, optional): Required if `challenge_type` is `CODING`. The programming language expected for the user-submitted code (e.g., `python3`, `nodejs`, `bash`, `dart`, `haskell`).
*   **`starter_code`** (string, optional): Optional starter code to display to the user for `CODING` challenges.
*   **`expected_output`** (string, optional): Required if `challenge_type` is `CODING`. The expected standard output (stdout) from the user's code for it to be considered solved.
*   **`setup_code`** (string, optional): Optional setup code/commands to run in the sandbox before the user's code for `CODING` challenges.
*   **`test_case_input`** (string, optional): Optional input to provide to the user's code via stdin for `CODING` challenges.
*   **`hint_cost`** (integer, optional): The default points deducted from a user's score when they reveal any hint associated with this challenge. This global cost applies if individual hints do not specify their own `cost`. Defaults to `0` (hints are free).
*   **`prerequisites`** (list of strings, optional): A list of challenge names (exact `name` strings) that must be solved by the user before this challenge becomes available. If specified, the `unlock_type` for this challenge will be internally set to `CHALLENGE_SOLVED`. This helps in creating dependency chains between challenges.
*   **`hints`** (list of objects, optional): A list of hint objects for the challenge, providing progressive assistance to users.
    *   **`title`** (string, required): The title of the hint, which is visible to the user before they choose to reveal the hint's content. Should be enticing but not spoil the solution.
    *   **`content`** (string, required): The actual hint text. This content is revealed to the user only after they choose to spend the `cost` associated with it. Supports markdown.
    *   **`cost`** (integer, optional): The specific point cost for revealing *this individual hint*. If not provided, the challenge's global `hint_cost` will be used. Defaults to `0` if neither is specified. Using individual hint costs allows for tiered hints (e.g., a cheap general clue, an expensive direct clue).

### Example YAML

```yaml
challenges:
  - name: "Warmup Challenge"
    description: |
      This is a simple warmup challenge designed to introduce new players to the platform.
      Find the flag hidden within this description or the challenge's provided files.

      **Hint**: The flag format is `flag{...}`.
    points: 50
    point_decay_type: "LINEAR" # Points decrease linearly after each solve
    point_decay_rate: 5        # 5 points deducted per solve
    minimum_points: 10         # Challenge will not be worth less than 10 points
    proactive_decay: true      # Points decay for all previous solvers as well
    hint_cost: 10              # Default hint cost for this challenge
    category: "General Skills"
    case_sensitive: true
    multi_flag_type: SINGLE
    flags:
      - "flag{welcome_to_windflag}"
    hints:
      - title: "First Clue"
        content: "The flag format is indeed `flag{...}`. Did you check the challenge description carefully?"
        cost: 5 # Override default hint_cost for this specific hint, making it cheaper
      - title: "Second Clue"
        content: "Look for a hidden message in the source code of the attached file or the challenge's webpage."
        cost: 15 # More expensive hint as it's more direct

  - name: "Coding Challenge: Python Sum"
    description: |
      Write a Python function that takes two numbers as input and returns their sum.
      The program should read two integers from stdin, and print their sum to stdout.
    points: 100
    category: "Programming"
    challenge_type: CODING
    language: python3
    starter_code: |
      def solve():
          # Read two numbers from stdin
          line1 = input()
          line2 = input()
          num1 = int(line1)
          num2 = int(line2)
          print(num1 + num2)

      if __name__ == "__main__":
          solve()
    expected_output: "30"
    setup_code: ""
    test_case_input: "10\n20"
    multi_flag_type: SINGLE # Coding challenges are usually single "flag" (solution)
    flags: [] # No flags needed for coding challenges

  - name: "Multi-Flag Web Challenge"
    description: |
      This web exploitation challenge requires finding several pieces of information
      scattered across different parts of a web application. You must find all of them
      to complete the challenge.
    points: 150
    category: "Web Exploitation"
    case_sensitive: false # Case-insensitive flag matching
    multi_flag_type: ALL # All defined flags must be submitted
    flags:
      - "flag{part_one_solved}"
      - "flag{part_two_complete}"
      - "flag{final_piece_found}"
    hints:
      - title: "Web Hint 1: Initial Recon"
        content: "Inspect the HTTP headers and cookies for unusual information."
      - title: "Web Hint 2: Hidden Endpoints"
        content: "There might be unlinked pages or API endpoints. Try common directory brute-forcing techniques."

  - name: "N-of-M Crypto Puzzle"
    description: |
      You've stumbled upon an encrypted message. To decrypt it, you need to find
      at least 2 out of 3 possible cryptographic keys. Each key is a flag.
    points: 200
    category: "Cryptography"
    multi_flag_type: N_OF_M # N out of M flags required
    multi_flag_threshold: 2 # Requires 2 flags to be submitted
    flags:
      - "flag{crypto_key_alpha}"
      - "flag{crypto_key_beta}"
      - "flag{crypto_key_gamma}"
    hints:
      - title: "Crypto Hint: Algorithm"
        content: "The encryption algorithm used is a variant of AES-256 with a common block cipher mode."
        cost: 25
      - title: "Crypto Hint: Key Derivation"
        content: "Consider how the keys might be derived from common passphrases or weak entropy sources."

  - name: "Dynamic Flag Challenge"
    description: |
      This challenge involves interacting with a remote service that generates a unique
      flag for each user. Your task is to correctly interact with the service and
      extract the flag.
    points: 300
    category: "Pwn"
    multi_flag_type: DYNAMIC # Flag is generated dynamically
    # No 'flags' field needed as it's dynamic
    hints:
      - title: "Dynamic Hint: Service Interaction"
        content: "The service listens on port 1337. Try `nc <host> 1337`."

  - name: "HTTP Flag Retrieval"
    description: |
      The flag for this challenge is located at a specific endpoint on an external server.
      You need to make the correct HTTP request to retrieve it.
    points: 100
    category: "Forensics"
    multi_flag_type: HTTP # Flag is retrieved via HTTP
    # No 'flags' field needed as it's HTTP
    # (Additional configuration for HTTP multi_flag_type would be handled in the backend, not YAML)
    hints:
      - title: "HTTP Hint: Endpoint"
        content: "The flag is at `/api/v1/flag`."

```

## How to Import Challenges via Command Line (CLI)

To import categories and challenges from a YAML file, use the `-yaml` or `-y` command-line argument when running `app.py`, followed by the path to your YAML file. Categories will be imported first, followed by challenges.

```bash
python app.py -yaml path/to/your/challenges.yaml
# or
python app.py -y path/to/your/challenges.yaml
```

**Important Notes for CLI Import:**
*   If a challenge or category with the same `name` already exists in the database, it will be skipped (no update).
*   Categories will be created automatically if they do not exist.
*   Ensure your YAML file is correctly formatted to avoid parsing errors.

## How to Import Challenges via API

You can also import challenges and categories in bulk via the administrative API. This is useful for integrating with external systems or automating challenge deployment.

**Endpoint:** `/api/admin/import/yaml`
**Method:** `POST`
**Authentication:** Requires an API key associated with an administrator user (`admin_api_required`).

**Request Body:**
The request body should be the raw YAML content containing the `categories` and/or `challenges` definitions.

**Example `curl` Command:**

```bash
curl -X POST -H "X-API-Key: YOUR_ADMIN_API_KEY" \
     -H "Content-Type: application/x-yaml" \
     --data-binary "@path/to/your/challenges.yaml" \
     http://127.0.0.1:5000/api/admin/import/yaml
```

*   Replace `YOUR_ADMIN_API_KEY` with an actual API key generated for an admin user.
*   Replace `path/to/your/challenges.yaml` with the actual path to your YAML file on your local system.
*   The `--data-binary` flag is used to send the raw file content as the request body.

**Example JSON Response (Success):**

```json
{
  "message": "YAML import completed successfully.",
  "details": [
    "Category 'Web Exploitation' (Pass 1) imported successfully.",
    "Category 'Forensics' (Pass 1) imported successfully.",
    "Category import process completed.",
    "Challenge 'Warmup 1' (Pass 1) imported successfully.",
    "Challenge 'Prereq Challenge' (Pass 2) prerequisites linked successfully.",
    "Challenge import process completed."
  ]
}
```

**Example JSON Response (Failure/Warnings):**

```json
{
  "message": "YAML import completed with errors or warnings. Check messages for details.",
  "details": [
    "Category 'Existing Category' already exists. Skipping import.",
    "Error: YAML source must contain a 'categories' key.",
    "Warning: Prerequisite challenge 'Unknown Challenge' for category 'My Category' not found. Skipping this prerequisite."
  ]
}
```

**Important Notes for API Import:**
*   Similar to CLI import, if a challenge or category with the same `name` already exists, it will be skipped.
*   Categories are imported before challenges.
*   Ensure the YAML content in your request body is valid.
*   Review the `details` field in the response for specific messages, warnings, or errors encountered during the import process.

## Importing Users from JSON

You can import user accounts from a JSON file using the `-users` or `-u` command-line argument.
