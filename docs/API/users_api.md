# User API Endpoints (Admin Only)

This section details the API endpoints for comprehensive user management within the WindFlag CTF Platform. These endpoints are primarily designed for administrators, allowing programmatic control over user accounts, roles, and related information.

## Authentication

All endpoints within the User API namespace are highly privileged and require administrator authentication. Access is granted via a user-generated API key, which must correspond to an account with administrative permissions.

*   **Mechanism**: The API key must be securely transmitted in the `X-API-KEY` HTTP header for every request.
*   **Permissions**: Only API keys belonging to users with `is_admin: true` (or `is_super_admin: true`) privileges will be authorized to access these endpoints.
*   **Further Details**: For more comprehensive information on API key generation, management, and authentication protocols, please refer to the [API Overview](./api_overview.md) documentation.

## 1. GET /api/users

Retrieves a paginated and filterable list of all registered users on the platform.

*   **Description**: This endpoint provides a comprehensive list of all user accounts. It's an essential tool for administrators to oversee the participant base, monitor user statuses, and prepare data for analytics or other management tasks. The response can be filtered, sorted, and paginated for efficient data handling.
*   **Method**: `GET`
*   **URL**: `/api/users`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Query Parameters**:
    *   `username_search` (string, optional): Performs a partial, case-insensitive search on usernames.
    *   `email_search` (string, optional): Performs a partial, case-insensitive search on email addresses.
    *   `is_admin` (boolean as "true"/"false", optional): Filters users by their administrator status.
    *   `is_super_admin` (boolean as "true"/"false", optional): Filters users by their super-administrator status.
    *   `is_hidden` (boolean as "true"/"false", optional): Filters users by their hidden status (hidden from public scoreboard).
    *   `has_api_key` (boolean as "true"/"false", optional): Filters users who currently have an active API key.
    *   `limit` (integer, optional): The maximum number of user records to return per page. Defaults to a platform-defined value (e.g., 20).
    *   `offset` (integer, optional): The number of user records to skip from the beginning of the result set. Useful for pagination.
    *   `sort_by` (string, optional): Field to sort the results by. Common values include `username`, `score`, `id`, `last_seen`. Defaults to `username`.
    *   `sort_order` (string, optional): Sort order, either `asc` (ascending) or `desc` (descending). Defaults to `asc`.
*   **Example Request**:
    ```http
    GET /api/users?is_admin=true&username_search=admin&sort_by=id&sort_order=asc HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "users": [
            {
                "id": 1,
                "username": "admin_main",
                "email": "admin@example.com",
                "score": 5000,
                "is_admin": true,
                "is_super_admin": true,
                "hidden": false,
                "last_seen": "2025-11-24T14:30:00Z",
                "member_since": "2023-01-15T09:00:00Z",
                "api_key_last_used": "2025-11-24T14:28:00Z"
            },
            {
                "id": 3,
                "username": "junior_admin",
                "email": "jr.admin@example.com",
                "score": 1200,
                "is_admin": true,
                "is_super_admin": false,
                "hidden": true,
                "last_seen": "2025-11-23T10:00:00Z",
                "member_since": "2024-03-01T11:00:00Z",
                "api_key_last_used": null
            }
        ],
        "total_users": 2,
        "limit": 10,
        "offset": 0
    }
    ```
    *   Each object in the `users` array represents a user with detailed profile information.
    *   `id` (integer): Unique numerical identifier.
    *   `username` (string): User's chosen display name.
    *   `email` (string): User's email address.
    *   `score` (integer): User's current total score.
    *   `is_admin` (boolean): `true` if user has admin privileges.
    *   `is_super_admin` (boolean): `true` if user has super admin privileges.
    *   `hidden` (boolean): `true` if user is hidden from the public scoreboard.
    *   `last_seen` (string, ISO 8601): UTC timestamp of user's last activity.
    *   `member_since` (string, ISO 8601): UTC timestamp of account creation.
    *   `api_key_last_used` (string, ISO 8601, null): UTC timestamp of the last time this user's API key was used.
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to view all users.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 400 Bad Request)**:
    ```json
    {
        "message": "Invalid query parameter for 'is_admin'. Must be 'true' or 'false'.",
        "code": "BAD_REQUEST_VALIDATION"
    }
    ```

## 2. GET /api/users/<int:user_id>

Retrieves full detailed profile information for a single user.

*   **Description**: This endpoint returns comprehensive profile details for a specific user, identified by their unique ID. It's a critical administrative tool for reviewing individual user accounts, checking their status, performance, and historical data.
*   **Method**: `GET`
*   **URL**: `/api/users/{user_id}`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Path Parameters**:
    *   `user_id` (integer, required): The unique ID of the user to retrieve.
*   **Example Request**:
    ```http
    GET /api/users/1 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "id": 1,
        "username": "admin_main",
        "email": "admin@example.com",
        "score": 5000,
        "is_admin": true,
        "is_super_admin": true,
        "hidden": false,
        "last_seen": "2025-11-24T14:30:00Z",
        "member_since": "2023-01-15T09:00:00Z",
        "api_key_last_used": "2025-11-24T14:28:00Z",
        "email_confirmed": true,
        "timezone": "UTC"
    }
    ```
    *   **`id`** (integer): The unique numerical identifier for the user.
    *   **`username`** (string): The user's chosen display name.
    *   **`email`** (string): The user's registered email address.
    *   **`score`** (integer): The user's current total score.
    *   **`is_admin`** (boolean): `true` if the user possesses administrative privileges.
    *   **`is_super_admin`** (boolean): `true` if the user possesses super-administrative privileges (highest level of access).
    *   **`hidden`** (boolean): `true` if the user is hidden from the public scoreboard; `false` otherwise.
    *   **`last_seen`** (string, ISO 8601): The UTC timestamp of the user's last recorded activity on the platform.
    *   **`member_since`** (string, ISO 8601): The UTC timestamp indicating when the user's account was created.
    *   **`api_key_last_used`** (string, ISO 8601, null): The UTC timestamp of the last time this user's API key was successfully used, or `null` if never used.
    *   **`email_confirmed`** (boolean): `true` if the user's email address has been confirmed; `false` otherwise.
    *   **`timezone`** (string): The user's preferred timezone setting.
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to view user details.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "User with ID '999' not found.",
        "code": "USER_NOT_FOUND"
    }
    ```

## 3. POST /api/users

Creates a new user account.

*   **Description**: This endpoint allows an administrator to manually create a new user account programmatically. This can be useful for pre-registering participants, creating system accounts, or for testing purposes.
*   **Method**: `POST`
*   **URL**: `/api/users`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Request Body**: `application/json`
    *   **`username`** (string, required): The desired unique username for the new user.
    *   **`password`** (string, required): The plain-text password for the new user. This will be hashed securely upon creation.
    *   **`email`** (string, optional): The email address for the new user. Must be unique and valid.
    *   **`is_admin`** (boolean, optional): Set to `true` to grant administrator privileges. Defaults to `false`.
    *   **`is_super_admin`** (boolean, optional): Set to `true` to grant super-administrator privileges. Defaults to `false`. (Only a super admin can create other super admins).
    *   **`hidden`** (boolean, optional): Set to `true` to hide the user from the public scoreboard. Defaults to `false`.
    *   **`email_confirmed`** (boolean, optional): Set to `true` to mark the email as confirmed. Defaults to `false`.
    *   **`timezone`** (string, optional): Set the user's preferred timezone.
*   **Example Request**:
    ```http
    POST /api/users HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    Content-Type: application/json

    {
        "username": "new_api_user",
        "email": "new.user@example.com",
        "password": "strongpassword123",
        "is_admin": false,
        "hidden": false
    }
    ```
*   **Example Response (Success - 201 Created)**:
    ```json
    {
        "message": "User created successfully",
        "user": {
            "id": 10,
            "username": "new_api_user",
            "email": "new.user@example.com"
        }
    }
    ```
*   **Example Response (Error - 400 Bad Request - Missing Fields)**:
    ```json
    {
        "message": "Missing required fields: username, password.",
        "code": "BAD_REQUEST_MISSING_FIELDS"
    }
    ```
*   **Example Response (Error - 400 Bad Request - Invalid Data)**:
    ```json
    {
        "message": "Validation error: Email address is invalid.",
        "code": "BAD_REQUEST_VALIDATION"
    }
    ```
*   **Example Response (Error - 403 Forbidden - Not enough permissions)**:
    ```json
    {
        "message": "Only super administrators can create other super administrators.",
        "code": "ADMIN_PRIVILEGE_REQUIRED"
    }
    ```
*   **Example Response (Error - 409 Conflict)**:
    ```json
    {
        "message": "User with username 'existing_user' already exists.",
        "code": "USERNAME_CONFLICT"
    }
    ```

## 4. PUT /api/users/<int:user_id>

Updates an existing user's profile and status.

*   **Description**: This endpoint allows administrators to modify various attributes of a specific user identified by their ID. It supports partial updates; only the fields included in the JSON payload will be updated. This flexibility enables granular changes to user profiles, roles, and administrative statuses.
*   **Method**: `PUT`
*   **URL**: `/api/users/{user_id}`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Path Parameters**:
    *   `user_id` (integer, required): The unique ID of the user to update.
*   **Request Body**: `application/json`. The body should contain a JSON object with the fields to update.
    *   **Updatable Fields**:
        *   **`username`** (string, optional): Updates the user's username. Must be unique.
        *   **`email`** (string, optional): Updates the user's email address. Must be unique and valid.
        *   **`password`** (string, optional): Sets a new password for the user. The new password will be hashed.
        *   **`is_admin`** (boolean, optional): Sets or revokes administrator privileges.
        *   **`is_super_admin`** (boolean, optional): Sets or revokes super-administrator privileges. (Only a super admin can grant/revoke super admin status).
        *   **`hidden`** (boolean, optional): Toggles whether the user is visible on the public scoreboard.
        *   **`score`** (integer, optional): Directly sets the user's score. Use with caution, as this bypasses normal scoring logic.
        *   **`email_confirmed`** (boolean, optional): Manually confirms or unconfirms the user's email address.
        *   **`timezone`** (string, optional): Sets the user's preferred timezone.
*   **Example Request (Change username and hide from scoreboard)**:
    ```http
    PUT /api/users/2 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    Content-Type: application/json

    {
        "username": "stealth_player",
        "hidden": true
    }
    ```
*   **Example Request (Grant admin privileges)**:
    ```http
    PUT /api/users/2 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_SUPER_ADMIN_API_KEY
    Content-Type: application/json

    {
        "is_admin": true
    }
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "message": "User updated successfully",
        "user_id": 2,
        "username": "stealth_player"
    }
    ```
    *   `message`: Confirmation message.
    *   `user_id`: The ID of the updated user.
    *   `username`: The new username of the user.
*   **Example Response (Error - 400 Bad Request - Invalid Data)**:
    ```json
    {
        "message": "Validation error: Email address is invalid.",
        "code": "BAD_REQUEST_VALIDATION"
    }
    ```
*   **Example Response (Error - 403 Forbidden - Not enough permissions)**:
    ```json
    {
        "message": "Only super administrators can modify super admin status.",
        "code": "ADMIN_PRIVILEGE_REQUIRED"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "User with ID '999' not found.",
        "code": "USER_NOT_FOUND"
    }
    ```
*   **Example Response (Error - 409 Conflict)**:
    ```json
    {
        "message": "User with username 'existing_user' already exists.",
        "code": "USERNAME_CONFLICT"
    }
    ```

## 5. DELETE /api/users/<int:user_id>

Deletes a specific user account.

*   **Description**: This endpoint allows an administrator to permanently remove a user account identified by its unique ID. This is a destructive operation that will also **cascade delete all associated data** for that user, including:
    *   All challenge submissions made by the user.
    *   All awards received by the user.
    *   Any hints revealed by the user.
    *   The user's API keys.
    *   **Caution**: This action is irreversible. Special care should be taken to ensure the correct user is being deleted.
*   **Method**: `DELETE`
*   **URL**: `/api/users/{user_id}`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Path Parameters**:
    *   `user_id` (integer, required): The unique ID of the user to delete.
*   **Example Request**:
    ```http
    DELETE /api/users/10 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Response (Success - 204 No Content)**:
    *   No content is returned in the response body, indicating successful deletion.
*   **Example Response (Error - 403 Forbidden - Cannot delete self)**:
    ```json
    {
        "message": "Administrators cannot delete their own account via API.",
        "code": "SELF_DELETE_FORBIDDEN"
    }
    ```
*   **Example Response (Error - 403 Forbidden - Cannot delete super admin)**:
    ```json
    {
        "message": "Only super administrators can delete other super administrators.",
        "code": "ADMIN_PRIVILEGE_REQUIRED"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "User with ID '999' not found.",
        "code": "USER_NOT_FOUND"
    }
    ```