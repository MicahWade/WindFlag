# Challenge API Endpoints

This section provides a detailed overview of the API endpoints dedicated to managing challenges within the WindFlag CTF Platform. These endpoints enable administrators to programmatically perform full CRUD (Create, Retrieve, Update, Delete) operations on challenges, and also facilitate user interactions such as flag submissions and hint revelation.

## Authentication

Access to most endpoints in the Challenge API namespace requires administrative authentication. User-facing endpoints (like flag submission or viewing unlocked challenges/hints) may only require regular user authentication, or in some cases, no authentication for public resources.

*   **Mechanism**: Authentication is typically handled via an `X-API-KEY` HTTP header.
*   **Permissions**:
    *   **Admin Endpoints**: Require API keys from users with `is_admin: true` (or `is_super_admin: true`).
    *   **User Endpoints**: Require API keys from any authenticated user.
*   **Further Details**: For more comprehensive information on API key generation, management, and authentication protocols, please refer to the [API Overview](./api_overview.md) documentation.

## 1. POST /api/challenges

Creates a new challenge within the CTF platform.

*   **Description**: This endpoint allows an administrator to define and create a new challenge by providing its complete details in a JSON payload. The structure of this payload mirrors the challenge definition found in the `docs/yaml.md` file, ensuring consistency across programmatic and YAML-based challenge creation. Robust validation is performed on all incoming fields.
*   **Method**: `POST`
*   **URL**: `/api/challenges`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Request Body**: `application/json`. The body should contain a JSON object representing the challenge.
    *   **`name`** (string, required): The unique name of the challenge. Must be unique across all challenges.
    *   **`description`** (string, required): A detailed description of the challenge, supporting markdown.
    *   **`points`** (integer, required): The initial points awarded for solving the challenge. Must be a positive integer.
    *   **`category_id`** (integer, required): The unique ID of the category this challenge belongs to. The category must exist.
    *   **`case_sensitive`** (boolean, optional): Whether flag submissions for this challenge are case-sensitive. Defaults to `true`.
    *   **`multi_flag_type`** (string, optional): Defines how multiple flags are handled. See `docs/yaml.md` for details.
        *   `SINGLE` (default), `ANY`, `ALL`, `N_OF_M`, `DYNAMIC`, `HTTP`.
    *   **`multi_flag_threshold`** (integer, optional): Required if `multi_flag_type` is `N_OF_M`. Specifies 'N' (the number of flags required).
    *   **`flags`** (array of strings, optional): A list of correct flag strings. Required for `SINGLE`, `ANY`, `ALL`, `N_OF_M`. Not used for `DYNAMIC` or `HTTP` flag types.
    *   **`hint_cost`** (integer, optional): Default points deducted for revealing a hint. Defaults to `0`.
    *   **`point_decay_type`** (string, optional): `STATIC` (default), `LINEAR`, or `LOGARITHMIC`. See `docs/yaml.md` for details.
    *   **`point_decay_rate`** (integer, optional): The rate of decay for `LINEAR` or `LOGARITHMIC` types.
    *   **`minimum_points`** (integer, optional): Minimum points a challenge can be worth due to decay. Defaults to `1`.
    *   **`proactive_decay`** (boolean, optional): Whether decay applies retroactively. Defaults to `false`.
    *   **`is_hidden`** (boolean, optional): If `true`, the challenge is hidden from non-admin users. Defaults to `false`.
    *   **`prerequisites`** (array of integers, optional): A list of challenge IDs that must be solved before this challenge unlocks.
    *   **`unlock_date_time`** (string, ISO 8601, optional): UTC datetime for timed unlock.
    *   **`dynamic_flag_api_url`** (string, optional): URL for the external dynamic flag service if `multi_flag_type` is `DYNAMIC` or `HTTP`.
    *   **`dynamic_flag_api_key`** (string, optional): API key for the external dynamic flag service if `multi_flag_type` is `DYNAMIC` or `HTTP`.
    *   **`hints`** (array of objects, optional): A list of hint objects. Each object should have:
        *   `title` (string, required): Hint title.
        *   `content` (string, required): Hint text.
        *   `cost` (integer, optional): Cost for this specific hint.
*   **Example Request**:
    ```http
    POST /api/challenges HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    Content-Type: application/json

    {
        "name": "API Created Web Exploit",
        "description": "Find the flag in this web challenge, deployed via API.",
        "points": 250,
        "category_id": 1,
        "case_sensitive": false,
        "multi_flag_type": "SINGLE",
        "flags": ["flag{api_web_challenge_success}"],
        "point_decay_type": "LOGARITHMIC",
        "point_decay_rate": 10,
        "minimum_points": 50,
        "hints": [
            {"title": "Web Hint 1", "content": "Check the source code.", "cost": 25}
        ],
        "is_hidden": false
    }
    ```
*   **Example Response (Success - 201 Created)**:
    ```json
    {
        "message": "Challenge created successfully",
        "challenge": {
            "id": 101,
            "name": "API Created Web Exploit",
            "points": 250,
            "category_id": 1
        }
    }
    ```
    *   `message`: Confirmation message.
    *   `challenge`: A partial object of the newly created challenge, including its `id`, `name`, `points`, and `category_id`.
*   **Example Response (Error - 400 Bad Request - Missing Fields)**:
    ```json
    {
        "message": "Missing required fields: name, description, points, category_id.",
        "code": "BAD_REQUEST_MISSING_FIELDS"
    }
    ```
*   **Example Response (Error - 400 Bad Request - Invalid Data)**:
    ```json
    {
        "message": "Validation error: Points must be a positive integer.",
        "code": "BAD_REQUEST_VALIDATION"
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to create challenges.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 409 Conflict)**:
    ```json
    {
        "message": "Challenge with name 'API Created Web Exploit' already exists.",
        "code": "CHALLENGE_NAME_CONFLICT"
    }
    ```

## 2. GET /api/challenges

Retrieves a paginated and filterable list of challenges available on the platform.

*   **Description**: This endpoint returns an array of challenge objects, allowing for flexible retrieval of challenge information. Administrators can view all challenges, including hidden ones, while regular users will only see challenges that are visible and unlocked for them. The response can be filtered, sorted, and paginated.
*   **Method**: `GET`
*   **URL**: `/api/challenges`
*   **Authentication**: `X-API-KEY` header (required). Admin users will see all challenges; regular users will see challenges based on their visibility and unlock status.
*   **Query Parameters**:
    *   `category_id` (integer, optional): Filters challenges belonging to a specific category ID.
    *   `category_name` (string, optional): Filters challenges belonging to a specific category name (case-insensitive).
    *   `is_hidden` (boolean as "true"/"false", optional): *Admin only*. Filters challenges by their hidden status.
    *   `unlocked_for_user_id` (integer, optional): Filters challenges that are unlocked for a specific user ID. *Admin only*.
    *   `solved_by_user_id` (integer, optional): Filters challenges that have been solved by a specific user ID. *Admin only*.
    *   `name_search` (string, optional): Performs a partial, case-insensitive search on challenge names.
    *   `limit` (integer, optional): The maximum number of challenges to return per page. Defaults to a platform-defined value.
    *   `offset` (integer, optional): The number of challenges to skip from the beginning of the result set. Useful for pagination.
    *   `sort_by` (string, optional): Field to sort the results by. Common values include `name`, `points`, `category_id`. Defaults to `name`.
    *   `sort_order` (string, optional): Sort order, either `asc` (ascending) or `desc` (descending). Defaults to `asc`.
*   **Example Request (Admin user, filter by category and hidden status)**:
    ```http
    GET /api/challenges?category_name=Web%20Exploitation&is_hidden=false&sort_by=points&sort_order=desc HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Request (Regular user, get first 10 challenges)**:
    ```http
    GET /api/challenges?limit=10 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_USER_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "challenges": [
            {
                "id": 2,
                "name": "Web Challenge 2",
                "description": "Exploit an XSS vulnerability.",
                "points": 200,
                "category_id": 1,
                "category_name": "Web Exploitation",
                "is_hidden": false,
                "is_solved": false,        // True if authenticated user solved it
                "is_unlocked": true,       // True if authenticated user can access it
                "solves": 15,              // Number of unique users who solved this
                "first_blood_user": "some_user",
                "point_decay_type": "LOGARITHMIC",
                "current_points": 180
            },
            {
                "id": 1,
                "name": "Web Challenge 1",
                "description": "Basic SQL Injection.",
                "points": 150,
                "category_id": 1,
                "category_name": "Web Exploitation",
                "is_hidden": false,
                "is_solved": true,
                "is_unlocked": true,
                "solves": 25,
                "first_blood_user": "another_user",
                "point_decay_type": "LINEAR",
                "current_points": 120
            }
        ],
        "total_challenges": 2,
        "limit": 10,
        "offset": 0
    }
    ```
    *   Each object in the `challenges` array provides summary information about a challenge.
    *   `is_solved` and `is_unlocked` are context-dependent for the authenticated user.
    *   `current_points` reflects the points after decay.
*   **Example Response (Error - 400 Bad Request)**:
    ```json
    {
        "message": "Invalid value for 'limit'. Must be a positive integer.",
        "code": "BAD_REQUEST_VALIDATION"
    }
    ```
*   **Example Response (Error - 403 Forbidden - Non-admin trying to use admin-only filters)**:
    ```json
    {
        "message": "Access denied. 'is_hidden' filter is for administrators only.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```

## 3. GET /api/challenges/<int:challenge_id>

Retrieves full details for a single challenge.

*   **Description**: This endpoint provides a comprehensive view of a specific challenge, identified by its unique ID. It includes all configuration details, associated hints, and current status relevant to the authenticated user.
*   **Method**: `GET`
*   **URL**: `/api/challenges/{challenge_id}`
*   **Authentication**: `X-API-KEY` header (required). Admin users can retrieve details for any challenge. Regular users can only retrieve details for challenges that are visible and unlocked for them.
*   **Path Parameters**:
    *   `challenge_id` (integer, required): The unique ID of the challenge to retrieve.
*   **Example Request**:
    ```http
    GET /api/challenges/101 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_USER_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "id": 101,
        "name": "API Created Web Exploit",
        "description": "Find the flag in this web challenge, deployed via API.",
        "points": 250,
        "category_id": 1,
        "category_name": "Web Exploitation",
        "case_sensitive": false,
        "multi_flag_type": "SINGLE",
        "multi_flag_threshold": null,
        "flags": [
            {"id": 1, "content": "flag{api_web_challenge_success}"}
        ],
        "point_decay_type": "LOGARITHMIC",
        "point_decay_rate": 10,
        "minimum_points": 50,
        "proactive_decay": false,
        "is_hidden": false,
        "dynamic_flag_api_url": null,
        "dynamic_flag_api_key_set": false, // Indicates if dynamic flag API key is configured (admin only)
        "hints": [
            {
                "id": 1,
                "title": "Web Hint 1",
                "content": "Check the source code.",
                "cost": 25,
                "is_revealed": true // True if the authenticated user has revealed this hint
            },
            {
                "id": 2,
                "title": "Web Hint 2",
                "content": null, // Content is null if not revealed by the user
                "cost": 50,
                "is_revealed": false
            }
        ],
        "prerequisites_met": true, // Indicates if prerequisites are met for the authenticated user
        "is_solved": false,        // True if the authenticated user has solved this challenge
        "is_unlocked": true,       // True if the authenticated user can access this challenge
        "solves": 5,               // Number of unique users who solved this challenge
        "current_points": 230,     // Current points for the challenge after decay
        "first_blood_user": "some_ctf_player",
        "created_at": "2025-11-24T10:00:00Z",
        "updated_at": "2025-11-24T11:00:00Z"
    }
    ```
    *   **`id`** (integer): Unique identifier for the challenge.
    *   **`name`** (string): Name of the challenge.
    *   **`description`** (string): Detailed description of the challenge (supports markdown).
    *   **`points`** (integer): Initial points value.
    *   **`category_id`** (integer): ID of the associated category.
    *   **`category_name`** (string): Name of the associated category.
    *   **`case_sensitive`** (boolean): Whether flag submission is case-sensitive.
    *   **`multi_flag_type`** (string): Type of flag handling (e.g., "SINGLE", "ALL", "DYNAMIC").
    *   **`multi_flag_threshold`** (integer, null): 'N' in 'N_OF_M' flag type, otherwise `null`.
    *   **`flags`** (array of objects): A list of flag objects. For regular users, `content` might be `null` or redacted for security. For admins, it shows the actual flag content.
        *   `id` (integer): ID of the flag.
        *   `content` (string): The flag string.
    *   **`point_decay_type`** (string): Type of point decay.
    *   **`point_decay_rate`** (integer): Rate of point decay.
    *   **`minimum_points`** (integer): Minimum points for the challenge.
    *   **`proactive_decay`** (boolean): Whether proactive decay is enabled.
    *   **`is_hidden`** (boolean): Whether the challenge is hidden from non-admins.
    *   **`dynamic_flag_api_url`** (string, null): URL for the dynamic flag API (admin only, or `null` if not dynamic).
    *   **`dynamic_flag_api_key_set`** (boolean): `true` if a dynamic flag API key is set (admin only, does not expose the key itself).
    *   **`hints`** (array of objects): List of hint objects.
        *   `id` (integer): ID of the hint.
        *   `title` (string): Title of the hint.
        *   `content` (string, null): Content of the hint. `null` if not yet revealed by the authenticated user.
        *   `cost` (integer): Cost to reveal this hint.
        *   `is_revealed` (boolean): `true` if the authenticated user has revealed this hint.
    *   **`prerequisites_met`** (boolean): `true` if the authenticated user has met all prerequisites for this challenge.
    *   **`is_solved`** (boolean): `true` if the authenticated user has solved this challenge.
    *   **`is_unlocked`** (boolean): `true` if the authenticated user can currently access this challenge.
    *   **`solves`** (integer): The total number of unique users who have solved this challenge.
    *   **`current_points`** (integer): The current point value of the challenge, reflecting any point decay.
    *   **`first_blood_user`** (string, null): The username of the user who achieved the first solve, or `null`.
    *   **`created_at`** (string, ISO 8601): UTC timestamp when the challenge was created.
    *   **`updated_at`** (string, ISO 8601): UTC timestamp when the challenge was last updated.
*   **Example Response (Error - 401 Unauthorized)**:
    ```json
    {
        "message": "Invalid or inactive API Key. Authentication required.",
        "code": "AUTH_REQUIRED"
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Access denied. Challenge not unlocked for this user.",
        "code": "CHALLENGE_LOCKED"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Challenge with ID '999' not found.",
        "code": "CHALLENGE_NOT_FOUND"
    }
    ```

## 4. PUT /api/challenges/<int:challenge_id>

Updates an existing challenge with new information.

*   **Description**: This endpoint allows administrators to modify the details of a specific challenge identified by its ID. It supports partial updates; only the fields included in the JSON payload will be updated. This flexibility enables granular changes without requiring a full re-submission of all challenge data. Special care is needed when updating `flags`, as providing a new `flags` array will *completely replace* all existing flags for that challenge.
*   **Method**: `PUT`
*   **URL**: `/api/challenges/{challenge_id}`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Path Parameters**:
    *   `challenge_id` (integer, required): The unique ID of the challenge to update.
*   **Request Body**: `application/json`. The body should contain a JSON object with the fields to update. All fields listed under `POST /api/challenges` can be used here, but only those provided will be modified.
    *   **Updating Flags**: If the `flags` field is included in the request body, all existing flags for the specified challenge will be deleted and replaced with the new flags provided in the array. If `flags` is omitted, existing flags remain unchanged.
*   **Example Request (Partial Update)**:
    ```http
    PUT /api/challenges/101 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    Content-Type: application/json

    {
        "description": "Updated description for API challenge, now with more details.",
        "points": 120,
        "is_hidden": true
    }
    ```
*   **Example Request (Update Flags)**:
    ```http
    PUT /api/challenges/101 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    Content-Type: application/json

    {
        "flags": ["flag{updated_api_flag_new_version}", "flag{another_new_flag}"]
    }
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "message": "Challenge updated successfully",
        "challenge_id": 101,
        "name": "API Created Web Exploit"
    }
    ```
    *   `message`: Confirmation message.
    *   `challenge_id`: The ID of the updated challenge.
    *   `name`: The name of the updated challenge.
*   **Example Response (Error - 400 Bad Request - Invalid Data)**:
    ```json
    {
        "message": "Validation error: Points must be a positive integer.",
        "code": "BAD_REQUEST_VALIDATION"
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to update challenges.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Challenge with ID '999' not found.",
        "code": "CHALLENGE_NOT_FOUND"
    }
    ```
*   **Example Response (Error - 409 Conflict)**:
    ```json
    {
        "message": "Challenge with name 'Another existing name' already exists.",
        "code": "CHALLENGE_NAME_CONFLICT"
    }
    ```

## 5. DELETE /api/challenges/<int:challenge_id>

Deletes a specific challenge from the platform.

*   **Description**: This endpoint allows an administrator to permanently remove a challenge identified by its unique ID. This is a destructive operation that will also **cascade delete all associated data**, including:
    *   All flags belonging to the challenge.
    *   All submissions made for this challenge.
    *   All hints associated with the challenge.
    *   Any other related data (e.g., dynamic flag API keys, prerequisites referencing this challenge).
    *   **Caution**: This action is irreversible.
*   **Method**: `DELETE`
*   **URL**: `/api/challenges/{challenge_id}`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Path Parameters**:
    *   `challenge_id` (integer, required): The unique ID of the challenge to delete.
*   **Example Request**:
    ```http
    DELETE /api/challenges/101 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Response (Success - 204 No Content)**:
    *   No content is returned in the response body, indicating successful deletion.
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to delete challenges.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Challenge with ID '999' not found.",
        "code": "CHALLENGE_NOT_FOUND"
    }
    ```

## 6. POST /api/challenges/<int:challenge_id>/submit

Allows an authenticated user to submit a flag or code for a challenge.

*   **Description**: This is the primary endpoint for users to attempt solving a challenge, whether it's a traditional flag submission or a coding challenge. For coding challenges, the submitted code undergoes rigorous server-side static analysis to detect and prevent malicious patterns or forbidden operations before execution. The submitted flag/code is then validated, and the user's score is updated accordingly if the submission is correct. This endpoint also handles cooldowns and rate limiting for submissions.
*   **Method**: `POST`
*   **URL**: `/api/challenges/{challenge_id}/submit`
*   **Authentication**: `X-API-KEY` header (required, any authenticated user)
*   **Path Parameters**:
    *   `challenge_id` (integer, required): The unique ID of the challenge to submit a flag for.
*   **Request Body**: `application/json`
    *   **`flag`** (string, required): The flag string submitted by the user (for traditional challenges).
    *   **`code`** (string, required): The code submitted by the user (for coding challenges). This field should be used when `challenge.challenge_type` is 'CODING'.
*   **Example Request (Traditional Flag)**:
    ```http
    POST /api/challenges/101/submit HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_USER_API_KEY
    Content-Type: application/json

    {
        "flag": "flag{api_web_challenge_success}"
    }
    ```
*   **Example Request (Coding Challenge)**:
    ```http
    POST /api/challenges/102/submit HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_USER_API_KEY
    Content-Type: application/json

    {
        "code": "print('Hello, world!')"
    }
    ```
*   **Example Response (Success - 200 OK - Correct Flag/Code)**:
    ```json
    {
        "message": "Flag submitted successfully! Challenge solved!",
        "is_correct": true,
        "new_score": 1500,
        "points_earned": 230,
        "stdout": "Hello, world!",
        "stderr": ""
    }
    ```
    *   `message`: A message indicating the result of the submission.
    *   `is_correct` (boolean): `true` if the flag/code was correct, `false` otherwise.
    *   `new_score` (integer): The user's updated total score after the submission.
    *   `points_earned` (integer): The points gained from this particular submission (relevant for correct flags/code).
    *   `stdout` (string, optional): The standard output of the executed code (for coding challenges).
    *   `stderr` (string, optional): The standard error of the executed code (for coding challenges).
*   **Example Response (Success - 200 OK - Incorrect Flag/Code)**:
    ```json
    {
        "message": "Incorrect flag. Try again!",
        "is_correct": false,
        "stdout": "Your code produced incorrect output.",
        "stderr": ""
    }
    ```
*   **Example Response (Error - 400 Bad Request - Missing fields)**:
    ```json
    {
        "message": "Request body must be JSON and include 'flag' or 'code'.",
        "code": "BAD_REQUEST_MISSING_FIELD"
    }
    ```
*   **Example Response (Error - 400 Bad Request - Static Analysis Failure)**:
    ```json
    {
        "message": "Security check failed: Forbidden import 'os' detected in code. This is not allowed for security reasons.",
        "code": "STATIC_ANALYSIS_FAILED"
    }
    ```
*   **Example Response (Error - 401 Unauthorized)**:
    ```json
    {
        "message": "Authentication required to submit flags.",
        "code": "AUTH_REQUIRED"
    }
    ```
*   **Example Response (Error - 403 Forbidden - Challenge Locked)**:
    ```json
    {
        "message": "Challenge is currently locked or hidden.",
        "code": "CHALLENGE_LOCKED"
    }
    ```
*   **Example Response (Error - 429 Too Many Requests - Cooldown/Rate Limit)**:
    ```json
    {
        "message": "Please wait before submitting another flag.",
        "retry_after_seconds": 5,
        "code": "TOO_MANY_REQUESTS"
    }
    ```

## 7. GET /api/challenges/<int:challenge_id>/hints

Retrieves a list of available hints for a specific challenge.

*   **Description**: Returns a list of hint objects for the specified challenge. For each hint, it indicates whether the authenticated user has already revealed its content. The actual content of unrevealed hints is omitted.
*   **Method**: `GET`
*   **URL**: `/api/challenges/{challenge_id}/hints`
*   **Authentication**: `X-API-KEY` header (required, any authenticated user)
*   **Path Parameters**:
    *   `challenge_id` (integer, required): The unique ID of the challenge to retrieve hints for.
*   **Example Request**:
    ```http
    GET /api/challenges/101/hints HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_USER_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "hints": [
            {
                "id": 1,
                "title": "Web Hint 1",
                "cost": 25,
                "is_revealed": true,
                "content": "Check the source code." // Content visible if revealed
            },
            {
                "id": 2,
                "title": "Web Hint 2",
                "cost": 50,
                "is_revealed": false,
                "content": null // Content is null if not yet revealed
            }
        ]
    }
    ```
*   **Example Response (Error - 401 Unauthorized)**:
    ```json
    {
        "message": "Authentication required to view hints.",
        "code": "AUTH_REQUIRED"
    }
    ```
*   **Example Response (Error - 403 Forbidden - Challenge Locked)**:
    ```json
    {
        "message": "Challenge is currently locked or hidden.",
        "code": "CHALLENGE_LOCKED"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Challenge with ID '999' not found.",
        "code": "CHALLENGE_NOT_FOUND"
    }
    ```

## 8. POST /api/challenges/<int:challenge_id>/hints/<int:hint_id>/reveal

Reveals the content of a specific hint for an authenticated user, deducting its cost.

*   **Description**: Allows an authenticated user to reveal a hint for a challenge. The cost of the hint is deducted from the user's score. Once revealed, the hint's content will be visible in subsequent `GET /api/challenges/<int:challenge_id>` and `GET /api/challenges/<int:challenge_id>/hints` responses.
*   **Method**: `POST`
*   **URL**: `/api/challenges/{challenge_id}/hints/{hint_id}/reveal`
*   **Authentication**: `X-API-KEY` header (required, any authenticated user)
*   **Path Parameters**:
    *   `challenge_id` (integer, required): The ID of the challenge the hint belongs to.
    *   `hint_id` (integer, required): The ID of the hint to reveal.
*   **Request Body**: (Empty or optional JSON for future extensions)
*   **Example Request**:
    ```http
    POST /api/challenges/101/hints/2/reveal HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_USER_API_KEY
    Content-Type: application/json
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "message": "Hint revealed successfully. Your score has been updated.",
        "hint_id": 2,
        "cost_deducted": 50,
        "new_score": 1450,
        "hint_content": "The flag is in the database, table 'secrets'."
    }
    ```
    *   `message`: Confirmation message.
    *   `hint_id` (integer): The ID of the revealed hint.
    *   `cost_deducted` (integer): The points deducted for revealing the hint.
    *   `new_score` (integer): The user's updated total score.
    *   `hint_content` (string): The revealed content of the hint.
*   **Example Response (Error - 401 Unauthorized)**:
    ```json
    {
        "message": "Authentication required to reveal hints.",
        "code": "AUTH_REQUIRED"
    }
    ```
*   **Example Response (Error - 403 Forbidden - Not Enough Points)**:
    ```json
    {
        "message": "You do not have enough points to reveal this hint.",
        "required_points": 50,
        "current_points": 20,
        "code": "INSUFFICIENT_POINTS"
    }
    ```
*   **Example Response (Error - 403 Forbidden - Challenge Locked)**:
    ```json
    {
        "message": "Challenge is currently locked or hidden.",
        "code": "CHALLENGE_LOCKED"
    }
    ```
*   **Example Response (Error - 404 Not Found - Challenge or Hint)**:
    ```json
    {
        "message": "Hint with ID '999' for challenge '101' not found.",
        "code": "HINT_NOT_FOUND"
    }
    ```
*   **Example Response (Error - 409 Conflict - Hint Already Revealed)**:
    ```json
    {
        "message": "This hint has already been revealed.",
        "code": "HINT_ALREADY_REVEALED"
    }
    ```