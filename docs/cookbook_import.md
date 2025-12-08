# Challenge Import Cookbook

This cookbook provides "recipes" for common challenge types and setups using the WindFlag YAML import format. For the full specification of all available fields, please refer to [yaml.md](yaml.md).

## Recipe 1: The Basic Flag Challenge

This is the most common type of challenge: a description, a single correct flag, and a category.

- **`name`** (string, required): The unique name of the challenge.
- **`description`** (string, required): A detailed explanation of the challenge, supporting markdown.
- **`category`** (string, optional): The name of the category the challenge belongs to. If not defined, "Uncategorized" is used.
- **`points`** (integer, required): The initial points awarded for solving the challenge.
- **`flags`** (list of strings, optional): A list of all correct flag strings for the challenge. Not required for `DYNAMIC` or `HTTP` flag types.

```yaml
challenges:
  - name: "Sanity Check"
    description: "Welcome to the CTF! The flag is in the topic."
    category: "Misc"
    points: 10
    flags:
      - "flag{sanity_check_passed}"
```

## Recipe 2: The "Hidden" Challenge

A challenge that rewards players for digging deeper. It uses case-insensitive matching and provides a hint that costs points.

- **`case_sensitive`** (boolean, optional): Determines whether the flag submission must match the case of the defined `flags`. Defaults to `true`.
- **`hint_cost`** (integer, optional): The default points deducted from a user's score when they reveal any hint for this challenge. Defaults to `0`.
- **`hints`** (list of objects, optional): A list of hint objects for the challenge.
  - **`title`** (string, required): The title of the hint, visible before content is revealed.
  - **`content`** (string, required): The actual hint text, supports markdown.
  - **`cost`** (integer, optional): Specific point cost for *this individual hint*, overriding `hint_cost`.

```yaml
challenges:
  - name: "Hidden in Plain Sight"
    description: "Can you find the secret hidden in the HTML source of the homepage?"
    category: "Web"
    points: 100
    case_sensitive: false  # "Flag{...}" and "flag{...}" both work
    hint_cost: 10          # Deduct 10 points for using the hint
    hints:
      - title: "Where to look"
        content: "Right-click -> View Page Source is your friend."
    flags:
      - "flag{html_comments_are_not_secure}"
```

## Recipe 3: The Coding Challenge

A challenge that requires the user to write code (e.g., Python) to solve a problem. The platform runs their code against a test case.

- **`challenge_type`** (string, optional): The type of challenge. Defaults to `FLAG`.
    - `FLAG`: Standard CTF challenge requiring a text flag.
    - `CODING`: Challenge requiring code submission, executed against a test case.
- **`language`** (string, optional): Required if `challenge_type` is `CODING`. The programming language expected for the user-submitted code (e.g., `python3`, `nodejs`, `bash`).
- **`test_case_input`** (string, optional): Optional input to provide to the user's code via stdin for `CODING` challenges.
- **`expected_output`** (string, optional): Required if `challenge_type` is `CODING`. The expected standard output (stdout) from the user's code.
- **`starter_code`** (string, optional): Optional starter code to display to the user for `CODING` challenges.

```yaml
challenges:
  - name: "Adder"
    description: "Write a Python script that reads two numbers from stdin and prints their sum."
    category: "Programming"
    points: 200
    challenge_type: "CODING"
    language: "python3"
    test_case_input: "5\n7"    # Input fed to the user's script
    expected_output: "12"      # Expected stdout from the user's script
    starter_code: |
      import sys
      
      def solve():
          # TODO: Read two lines from sys.stdin
          # TODO: Print the sum
          pass
      
      if __name__ == "__main__":
          solve()
```

## Recipe 4: The Scavenger Hunt (N-of-M Flags)

A challenge where users need to find a subset of multiple hidden flags. Great for OSINT or exploration tasks.

- **`multi_flag_type`** (string, optional): Defines how multiple flags are handled. Defaults to `SINGLE`.
    - `SINGLE`: One correct flag solves the challenge.
    - `ANY`: Any one of the listed flags solves the challenge.
    - `ALL`: All listed flags must be submitted to solve the challenge.
    - `N_OF_M`: A specific number (N) of the listed flags (M) must be submitted.
    - `DYNAMIC`: Flag is generated/validated by custom logic (not defined in list).
    - `HTTP`: Flag is retrieved from an external URL.
- **`multi_flag_threshold`** (integer, optional): Required if `multi_flag_type` is `N_OF_M`. Specifies the number of flags ('N') required to solve the challenge.

```yaml
challenges:
  - name: "Social Butterfly"
    description: |
      We have hidden 5 flags across our social media profiles.
      Find at least **3** of them to solve this challenge.
    category: "OSINT"
    points: 150
    multi_flag_type: "N_OF_M"
    multi_flag_threshold: 3    # User needs 3 out of the 5 flags
    flags:
      - "flag{twitter_bio}"
      - "flag{instagram_story}"
      - "flag{linkedin_post}"
      - "flag{discord_status}"
      - "flag{youtube_comment}"
```

## Recipe 5: The "Boss" Challenge (Decay & Prerequisites)

A high-value challenge that decays in value as more people solve it, and requires previous challenges to be solved first.

- **`minimum_points`** (integer, optional): The lowest number of points a challenge can be worth due to decay. Defaults to `1`.
- **`point_decay_type`** (string, optional): The strategy for how the challenge's point value decreases as more users solve it. Defaults to `STATIC`.
    - `STATIC`: Points do not change.
    - `LINEAR`: Points decrease by `point_decay_rate` per solve.
    - `LOGARITHMIC`: Points decrease quickly at first, then slower, based on solve count.
- **`point_decay_rate`** (integer, optional): The rate of decay for `LINEAR` or `LOGARITHMIC` decay types.
- **`proactive_decay`** (boolean, optional): If `true`, points for this challenge will decay for *all* users (including those who have already solved it) when a new user solves it. Defaults to `false`.
- **`prerequisites`** (list of strings, optional): A list of challenge names that must be solved before this challenge becomes available.

```yaml
challenges:
  - name: "The Final Boss"
    description: "The hardest binary exploitation challenge in the CTF."
    category: "Pwn"
    points: 1000
    minimum_points: 100
    point_decay_type: "LOGARITHMIC"  # Points drop quickly then level off
    point_decay_rate: 10
    proactive_decay: true            # Updates score for users who already solved it
    prerequisites:
      - "Buffer Overflow 101"        # Must solve this challenge first
      - "Heap Exploitation"          # AND this one
    flags:
      - "flag{y0u_h4v3_c0nqu3r3d_th3_b1n4ry}"
```

## Recipe 6: Timed & Locked Categories

A setup for a category that only opens at a specific time or after the user has progressed enough in other areas.

- **`unlock_type`** (string, optional): The type of unlocking mechanism for the category. Defaults to `NONE`.
    - `NONE`: Category is always available.
    - `PREREQUISITE_PERCENTAGE`: Unlocks after a % of all/category challenges are solved.
    - `PREREQUISITE_COUNT`: Unlocks after a specific number of challenges are solved.
    - `PREREQUISITE_CHALLENGES`: Unlocks after specific named challenges are solved.
    - `TIMED`: Unlocks at a specific UTC date/time.
    - `COMBINED`: Allows combining multiple conditions (e.g., Time AND Percentage).
- **`unlock_date_time`** (string, optional): Required if `unlock_type` is `TIMED` or `COMBINED`. The UTC datetime string (e.g., "YYYY-MM-DDTHH:MM:SSZ").
- **`is_hidden`** (boolean, optional): If `true`, the category will be entirely hidden from non-admin users until its unlock conditions are met. Defaults to `false`.
- **`prerequisite_percentage_value`** (integer, optional): Required if `unlock_type` is `PREREQUISITE_PERCENTAGE` or `COMBINED`. An integer between 1 and 100 representing the percentage of challenges that must be solved.

```yaml
categories:
  - name: "Late Night Special"
    description: "Challenges that unlock only at midnight."
    unlock_type: "TIMED"
    unlock_date_time: "2025-10-31T23:59:00Z" # UTC Time
    is_hidden: true                         # Category is invisible until unlock time

  - name: "Elite Zone"
    description: "Only accessible after solving 50% of all other challenges."
    unlock_type: "PREREQUISITE_PERCENTAGE"
    prerequisite_percentage_value: 50

challenges:
  - name: "Midnight Cipher"
    category: "Late Night Special" # Assigned to the timed category
    points: 300
    description: "The moon is high..."
    flags:
      - "flag{werewolf}"
```

## Recipe 7: Project Structure for Challenge Packs

Organize multiple challenges into a single "Pack" controlled by one `import.yaml`. This is the recommended structure.

**Directory Structure:**
```text
LinuxBasics/
├── import.yaml          <-- One file defining ALL challenges
├── level_1/             <-- Folder for Challenge 1 (Dockerfile)
│   ├── Dockerfile
│   └── solve.yaml
├── level_2/             <-- Folder for Challenge 2 (Dockerfile)
│   ├── Dockerfile
│   └── solve.yaml
└── level_3/             <-- Folder for Challenge 3
    ├── Dockerfile
    └── solve.yaml
```

**Content of `import.yaml`:**
```yaml
challenges:
  - name: "Linux Basics Level 1"
    image: "level_1"     # Points to the 'level_1' folder
    description: "..."
    points: 10
    flags: ["flag{one}"]

  - name: "Linux Basics Level 2"
    image: "level_2"     # Points to the 'level_2' folder
    description: "..."
    points: 20
    flags: ["flag{two}"]
```

**Bundling Command:**
```bash
# Bundle the specific pack
python3 -m prism.cli bundle ./LinuxBasics --output ./linux_basics.zip
```