# Challenge Import Cookbook

This cookbook provides "recipes" for common challenge types and setups using the WindFlag YAML import format. For the full specification of all available fields, please refer to [yaml.md](yaml.md).

## Recipe 1: The Basic Flag Challenge

This is the most common type of challenge: a description, a single correct flag, and a category.

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