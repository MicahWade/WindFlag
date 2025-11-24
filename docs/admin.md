# Admin Panel Challenge Visibility

The Admin Panel's "Manage Challenges" section provides enhanced visual cues to help administrators quickly understand the visibility and accessibility status of each challenge at a glance. These challenges may appear with different background "stripes" (colors) to indicate their current state based on configuration and user progression. Understanding these indicators is crucial for effective CTF management and ensuring a smooth player experience.

## Interpreting Challenge Visibility Stripes

Each challenge in the table can display one of the following visual indicators, which are prioritized for display (Red > Orange > Yellow > Blue):

*   **<span style="background-color: rgba(220, 38, 38, 0.5); padding: 2px 5px; border-radius: 3px;">Red Stripe (Hidden / Locked for All Users)</span>**
    *   **Meaning**: This is the most restrictive state. A red stripe indicates that the challenge is *currently inaccessible to all non-admin users*. This can be due to several reasons:
        *   The challenge itself is explicitly marked as `is_hidden = True` in its settings.
        *   The category to which the challenge belongs is hidden (`is_hidden = True`) or has a `TIMED` unlock type with a future `unlock_date_time`.
        *   The challenge has a `TIMED` unlock type with a future `unlock_date_time`.
    *   **Implication for Users**: Non-admin users will not see this challenge listed on the challenges page. If they try to access it directly (e.g., via a URL), they will be denied.
    *   **Admin Action**: To make a red-striped challenge available, administrators must navigate to the challenge's (or its category's) edit page and adjust its `is_hidden` status or its `unlock_date_time`.

*   **<span style="background-color: rgba(202, 138, 4, 0.5); padding: 2px 5px; border-radius: 3px;">Orange Stripe (Unlockable - No Solves Yet)</span>**
    *   **Meaning**: An orange stripe signifies that the challenge is *visible* to users but currently `locked` because *no eligible user has yet met its specific unlock prerequisites*. These prerequisites can include:
        *   Solving a certain percentage of challenges in a category (`PREREQUISITE_PERCENTAGE`).
        *   Solving a specific number of challenges (`PREREQUISITE_COUNT`).
        *   Solving a list of other named challenges (`PREREQUISITE_CHALLENGES`).
    *   **Implication for Users**: Users will see the challenge listed but will be unable to access its content or submit flags until they complete the specified prerequisites.
    *   **Admin Action**: This status is a good indicator of the initial difficulty or prerequisite bottleneck of a challenge. Administrators might consider adjusting the prerequisites if too few users are able to unlock it, or add hints to help users overcome the prerequisite challenges.

*   **<span style="background-color: rgba(252, 211, 77, 0.5); padding: 2px 5px; border-radius: 3px;">Yellow Stripe (Unlocked by 0-50% of Eligible Users)</span>**
    *   **Meaning**: A yellow stripe indicates that the challenge is *unlocked* (i.e., its prerequisites have been met) by *some* users, but by less than 50% of the eligible user base. This suggests the challenge is either new, particularly challenging, or requires specific knowledge that only a subset of players possess.
    *   **Implication for Users**: Players who meet the prerequisites can access and attempt the challenge.
    *   **Admin Action**: This status can help administrators identify challenges that are "hard but solvable" or those that might benefit from additional hints or clarification in their descriptions if the goal is to increase the solve rate.

*   **<span style="background-color: rgba(37, 99, 235, 0.5); padding: 2px 5px; border-radius: 3px;">Blue Stripe (Unlocked by 50-90% of Eligible Users)</span>**
    *   **Meaning**: A blue stripe indicates that the challenge is *unlocked* by a significant portion (50-90%) of the eligible user base. This suggests the challenge is well-integrated into the CTF flow and its difficulty is appropriate for a broad range of players.
    *   **Implication for Users**: Most players who have progressed sufficiently in the CTF will find this challenge accessible.
    *   **Admin Action**: Challenges in this state are generally healthy and contributing positively to the CTF experience. No specific action is typically required unless a deviation from expected solve rates is observed.

*   **No Stripe (Widely Unlocked / Freely Accessible)**
    *   **Meaning**: A challenge with no stripe is either freely accessible to all users (no unlock conditions) or has been unlocked by more than 90% of the eligible user base. It's a widely available and/or commonly solved challenge.
    *   **Implication for Users**: This challenge is broadly accessible.
    *   **Admin Action**: These challenges usually form the foundational or introductory parts of a CTF.

## Modifying Challenge Visibility and Unlock Conditions

Administrators can directly influence challenge visibility and unlock conditions through the Admin Panel:

1.  **Navigate to "Manage Challenges"**: From the Admin Panel dashboard, select the "Challenges" section.
2.  **Edit Challenge/Category**: Click the "Edit" button next to a specific challenge or navigate to "Manage Categories" to edit category settings.
3.  **Adjust Settings**:
    *   **`is_hidden`**: Toggle this boolean to directly hide or show a challenge/category.
    *   **`unlock_type`**: Select the desired unlock mechanism (e.g., `NONE`, `PREREQUISITE_PERCENTAGE`, `TIMED`).
    *   **Prerequisite Values**: Set `prerequisite_percentage_value`, `prerequisite_count_value`, `prerequisite_challenge_names`, or `unlock_date_time` as appropriate for the chosen `unlock_type`.
    *   **Save Changes**: Always remember to save your changes to apply the new settings.

## Dynamic Flags

The WindFlag platform offers robust support for dynamic flags, a powerful feature that enhances challenge security and fairness by providing a unique flag to each user. This mechanism prevents flag sharing and ensures that every participant must genuinely solve the challenge to obtain their individual flag.

### Configuration

To leverage dynamic flags for a challenge, follow these configuration steps within the Admin Panel:

1.  **Set Flag Type to "Dynamic"**: When creating a new challenge or editing an existing one, navigate to the "Flag Configuration" section. Set the "Flag Type" dropdown to "Dynamic". This action will automatically reveal a new "Dynamic Flag Settings" section on the challenge edit page, which is essential for further configuration.

2.  **Generate API Key**:
    *   Once the challenge is saved with the "Dynamic" flag type, revisit its edit page. In the "Dynamic Flag Settings" section, you will find a button labeled "Generate New Dynamic Flag API Key".
    *   Click this button to generate a unique API key specifically for this challenge.
    *   **Crucially, copy and save this generated API key immediately.** For security reasons, it will only be displayed *once* at the time of generation and cannot be retrieved again from the UI. If lost, you will need to generate a new key, invalidating the old one.

### Integrating with Your External Application

Your external application (which hosts the dynamic flag logic) must expose an HTTP endpoint designed to receive requests from the WindFlag platform and return a user-specific flag.

#### Endpoint Requirements

*   **Method**: Your endpoint should accept `POST` requests.
*   **Request Body**: The request will contain a JSON body with the following structure:
    ```json
    {
        "user_id": 123,
        "challenge_id": 456,
        "username": "example_user"
    }
    ```
    *   `user_id` (integer): The unique identifier for the user requesting the flag.
    *   `challenge_id` (integer): The unique identifier for the challenge being solved.
    *   `username` (string): The username of the user requesting the flag.
    You can use this information to generate a flag unique to the user and challenge.
*   **Request Header**: The WindFlag platform will include the generated API key in the `X-API-KEY` header of the request. Your application *must* validate this header to ensure the request originates from your WindFlag instance and is authorized.
    *   **Example Header**: `X-API-KEY: your_generated_api_key`
*   **Response**: Your endpoint should return a JSON response with a `flag` key, containing the dynamic flag for the user.
    *   **Example Response**:
    ```json
    {
        "flag": "flag{this_is_a_dynamic_flag_for_user_123_for_challenge_456}"
    }
    ```
*   **Error Handling**: If your external application encounters an error (e.g., cannot generate a flag, invalid request), it should return an appropriate HTTP status code (e.g., 400, 500) and an error message in the JSON response. WindFlag will log these errors for administrative review.

#### Example Request (from WindFlag to your endpoint)

```http
POST /your-dynamic-flag-endpoint HTTP/1.1
Host: your-dynamic-flag-service.com
Content-Type: application/json
X-API-KEY: your_generated_api_key_from_windflag

{
    "user_id": 123,
    "challenge_id": 456,
    "username": "player_one"
}
```

#### Example Response (from your endpoint to WindFlag)

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "flag": "flag{dynamic_challenge_flag_for_player_one_uid123}"
}
```

### Security Best Practices for Dynamic Flags

*   **API Key Protection**: Treat the generated API key as a sensitive secret. Store it securely within your external dynamic flag application (e.g., in environment variables, a secrets manager) and *never* hardcode it directly into your codebase.
*   **Endpoint Security**: Ensure your dynamic flag endpoint is properly secured against unauthorized access. Implement rate limiting, IP whitelisting (if possible, to only allow requests from your WindFlag server), and robust input validation.
*   **Unique Flags**: Generate truly unique flags for each user to maintain the integrity of the CTF. Avoid predictable patterns.
*   **Service Reliability**: Ensure your external dynamic flag service is highly available and responsive, as it directly impacts the user experience for dynamic flag challenges.
*   **Logging**: Implement comprehensive logging in your external service to monitor requests, flag generations, and any errors, which can aid in debugging and security auditing.

---

## Comprehensive Admin Panel Overview

The WindFlag Admin Panel is a centralized hub for managing all aspects of your Capture The Flag (CTF) event. It provides a powerful and intuitive interface for administrators to configure challenges, manage users, track progress, and customize platform settings. Access to the Admin Panel requires an account with administrative privileges.

### Admin Panel Sections

The Admin Panel is typically organized into several key sections, each dedicated to a specific management function:

1.  **Dashboard/Analytics**: Provides an overview of the CTF's status, including visual analytics on user scores, challenge solve rates, and other key metrics. (See `docs/API/analytics_api.md` for more details on available data).
2.  **Manage Users**: Tools for user account management.
3.  **Manage Categories**: For organizing challenges into logical groups.
4.  **Manage Challenges**: Comprehensive challenge creation, editing, and deletion.
5.  **Manage Award Categories**: Define and manage different types of awards.
6.  **Manage Awards**: Assign awards to users.
7.  **Settings**: Global platform configurations.
8.  **Themes**: Customizing the look and feel of the platform.

## User Management

The "Manage Users" section allows administrators to maintain the user base of the CTF platform.

*   **Viewing Users**: A table lists all registered users, displaying their usernames, email addresses, current scores, and administrative statuses.
*   **Creating New Users**:
    *   Administrators can manually create new user accounts directly from the Admin Panel.
    *   This is useful for adding special accounts (e.g., for judges, organizers) or for pre-populating the platform with participants.
    *   Fields typically include username, email, and password.
*   **Editing Existing Users**:
    *   **Roles**: Assign or revoke `is_admin` (standard administrator) and `is_super_admin` (super administrator) privileges. Super administrators have elevated permissions, including managing other admin accounts.
    *   **Hidden Status**: Toggle the `hidden` status to make a user's score and activity visible or invisible on the public scoreboard. This is useful for testing accounts or organizers who should not appear in the rankings.
    *   **Password Reset**: Administrators can initiate password resets for users.
    *   **Score Adjustment**: Manually adjust a user's score (e.g., for penalizing rule violations or granting bonus points).
*   **Deleting Users**: Administrators have the ability to permanently delete user accounts and all associated data (submissions, hints revealed, etc.). Exercise caution when performing this action.

## Category Management

The "Manage Categories" section empowers administrators to define and organize the logical structure of challenges within the CTF.

*   **Creating Categories**:
    *   Define new categories with unique names (e.g., "Web Exploitation," "Cryptography," "Forensics").
    *   Set **Unlock Types** (`NONE`, `PREREQUISITE_PERCENTAGE`, `PREREQUISITE_COUNT`, `PREREQUISITE_CHALLENGES`, `TIMED`, `COMBINED`) and their corresponding values. (Refer to `docs/yaml.md` for detailed explanations of these unlock types).
    *   Configure `is_hidden` to control initial visibility.
*   **Editing Categories**: Modify existing category names, descriptions, unlock types, prerequisite values, and hidden status. Changes to unlock conditions will dynamically affect when challenges within that category become available to users.
*   **Deleting Categories**: Remove categories. Note that challenges associated with a deleted category might become "Uncategorized" or require reassignment.

## Award Management

The "Award Management" sections (`Manage Award Categories` and `Manage Awards`) allow administrators to recognize and reward user achievements beyond regular challenge solves.

### Manage Award Categories

*   **Creating Award Categories**: Define different types or themes for awards (e.g., "First Blood," "Participation," "Bug Bounty," "Sportsmanship").
*   **Editing Award Categories**: Modify names and descriptions of existing categories.
*   **Deleting Award Categories**: Remove award categories.

### Manage Awards

*   **Granting Awards**: Assign specific awards to individual users.
    *   Select the recipient user.
    *   Choose an award category.
    *   Specify the points associated with the award (these points contribute to the user's total score).
    *   Add an optional description for the award.
*   **Revoking Awards**: Remove previously granted awards, which will adjust the user's score accordingly.

## System Settings

The "Settings" section provides control over global application configurations, allowing administrators to customize the CTF environment.

*   **General Settings**: Configure `APP_NAME`, `SECRET_KEY`, and other general application parameters (refer to `docs/ENV.md` for a comprehensive list of environment variables and their functions, many of which can be managed here).
*   **Registration Settings**: Adjust `REQUIRE_JOIN_CODE`, `JOIN_CODE`, `DISABLE_SIGNUP`, and `REQUIRE_EMAIL` directly from the UI.
*   **Scoreboard Settings**: Configure aspects of the scoreboard, such as whether hidden users are displayed to admins.
*   **Theming Options**: Select default themes or manage theme-related settings. (See `docs/themes.md` for more details).
*   **Maintenance Mode**: Enable or disable maintenance mode, which can be used to temporarily take the site offline for updates or critical fixes.

## Security Best Practices for Administrators

Effective administration of a CTF platform involves adhering to strong security practices to protect user data and the integrity of the competition.

*   **Strong Passwords**: Always use strong, unique passwords for administrator accounts. Consider using a password manager.
*   **Role-Based Access**: Assign administrative roles (`is_admin`, `is_super_admin`) judiciously. Grant the minimum necessary privileges required for each administrator's responsibilities.
*   **API Key Management**: Treat dynamic flag API keys (and any other API keys) as highly sensitive credentials. Never share them unnecessarily or embed them directly in public-facing code. Rotate them regularly.
*   **Regular Audits**: Periodically review user accounts, especially administrative ones, for any unauthorized access or suspicious activity.
*   **Data Handling**: Be mindful of sensitive user data. Do not export or share user information without proper authorization and security measures.
*   **Software Updates**: Keep the WindFlag application and its dependencies up-to-date to benefit from the latest security patches.
*   **Backup**: Regularly back up your database and challenge data.

By understanding and utilizing these administrative features and following security best practices, you can ensure a well-managed, secure, and engaging CTF experience for all participants.