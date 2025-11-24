# Award API Endpoints

This section details the API endpoints dedicated to managing awards given to users within the WindFlag CTF Platform. These powerful endpoints allow administrators to programmatically grant, retrieve, and manage awards, facilitating dynamic recognition of user achievements.

## Authentication

All endpoints within the Award API namespace are privileged and require administrator authentication. Access is granted via a user-generated API key, which must correspond to an account with administrative permissions.

*   **Mechanism**: The API key must be securely transmitted in the `X-API-KEY` HTTP header for every request.
*   **Permissions**: Only API keys belonging to users with `is_admin: true` (or `is_super_admin: true`) privileges will be authorized to access these endpoints.
*   **Further Details**: For more comprehensive information on API key generation, management, and authentication protocols, please refer to the [API Overview](./api_overview.md) documentation.

## 1. POST /api/awards

This endpoint facilitates the programmatic granting of an award to a specified user, associating it with an award category and a defined point value.

*   **Description**: This is the primary endpoint for administrators to issue awards. It allows for flexible recognition of user achievements by assigning points based on pre-defined award categories. Upon successful creation, the user's score will be updated to reflect the `points_awarded`.
*   **Method**: `POST`
*   **URL**: `/api/awards`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Request Body**: `application/json`
    *   **`user_id`** (integer, required): The unique numerical identifier (`id`) of the user who will receive the award. This ID corresponds to the `id` field of a user object.
    *   **`category_id`** (integer, required): The unique numerical identifier (`id`) of the award category to which this award belongs. Award categories define the type or nature of the award (e.g., "First Blood", "Participation").
    *   **`points_awarded`** (integer, required): The number of points associated with this specific award instance. These points will be added to the recipient user's total score. Must be a non-negative integer.
    *   **`description`** (string, optional): An optional, brief text description for this specific award instance (e.g., "For solving the hardest challenge first"). This can provide context beyond the category name.
    *   **`giver_id`** (integer, optional): The `id` of the administrator giving the award. If omitted, the `id` of the authenticated admin user making the API request will be used.
*   **Example Request**:
    ```http
    POST /api/awards HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    Content-Type: application/json

    {
        "user_id": 5,
        "category_id": 2,
        "points_awarded": 100,
        "description": "Awarded for outstanding contribution to team spirit."
    }
    ```
*   **Example Response (Success - 201 Created)**:
    ```json
    {
        "message": "Award given successfully",
        "award": {
            "id": 101,
            "user_id": 5,
            "username": "award_recipient",
            "category_id": 2,
            "category_name": "Teamwork Award",
            "points_awarded": 100,
            "description": "Awarded for outstanding contribution to team spirit.",
            "giver_id": 1,
            "giver_username": "admin_user",
            "timestamp": "2025-11-24T15:30:00Z"
        }
    }
    ```
    *   `id` (integer): The unique numerical identifier of the newly created award instance.
    *   `user_id` (integer): The ID of the user who received the award.
    *   `username` (string): The username of the award recipient.
    *   `category_id` (integer): The ID of the award category.
    *   `category_name` (string): The name of the award category.
    *   `points_awarded` (integer): The points granted by this award.
    *   `description` (string, optional): The specific description for this award instance.
    *   `giver_id` (integer): The ID of the administrator who granted the award.
    *   `giver_username` (string): The username of the administrator who granted the award.
    *   `timestamp` (string, ISO 8601): The UTC timestamp when the award was granted.
*   **Example Response (Error - 400 Bad Request)**:
    ```json
    {
        "message": "Invalid request body. Ensure all required fields (user_id, category_id, points_awarded) are present and correctly formatted.",
        "code": "BAD_REQUEST_VALIDATION"
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to grant awards.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 404 Not Found - User)**:
    ```json
    {
        "message": "User with ID '5' not found.",
        "code": "USER_NOT_FOUND"
    }
    ```
*   **Example Response (Error - 404 Not Found - Category)**:
    ```json
    {
        "message": "Award Category with ID '2' not found.",
        "code": "AWARD_CATEGORY_NOT_FOUND"
    }
    ```

## 2. GET /api/awards

Retrieves a list of all awards granted across the platform.

*   **Description**: This endpoint provides a comprehensive list of all awards that have been granted to users. It's useful for administrators to review all recognition events. Results can be filtered and paginated.
*   **Method**: `GET`
*   **URL**: `/api/awards`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Query Parameters**:
    *   `user_id` (integer, optional): Filter awards by a specific user ID.
    *   `category_id` (integer, optional): Filter awards by a specific award category ID.
    *   `giver_id` (integer, optional): Filter awards by the ID of the administrator who granted them.
    *   `limit` (integer, optional): The maximum number of awards to return per page. Defaults to a platform-defined value.
    *   `offset` (integer, optional): The number of awards to skip before starting to collect the result set.
*   **Example Request**:
    ```http
    GET /api/awards?user_id=5&limit=10 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "awards": [
            {
                "id": 101,
                "user_id": 5,
                "username": "award_recipient",
                "category_id": 2,
                "category_name": "Teamwork Award",
                "points_awarded": 100,
                "description": "Awarded for outstanding contribution to team spirit.",
                "giver_id": 1,
                "giver_username": "admin_user",
                "timestamp": "2025-11-24T15:30:00Z"
            },
            {
                "id": 102,
                "user_id": 5,
                "username": "award_recipient",
                "category_id": 1,
                "category_name": "First Blood",
                "points_awarded": 50,
                "description": "First solve of Web Challenge 1",
                "giver_id": 3,
                "giver_username": "another_admin",
                "timestamp": "2025-11-23T10:00:00Z"
            }
        ],
        "total_awards": 2,
        "limit": 10,
        "offset": 0
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to view all awards.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```

## 3. GET /api/awards/<int:award_id>

Retrieves detailed information for a specific award.

*   **Description**: Fetches the full details of a single award instance given its unique identifier.
*   **Method**: `GET`
*   **URL**: `/api/awards/{award_id}`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Path Parameters**:
    *   `award_id` (integer, required): The unique ID of the award to retrieve.
*   **Example Request**:
    ```http
    GET /api/awards/101 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "id": 101,
        "user_id": 5,
        "username": "award_recipient",
        "category_id": 2,
        "category_name": "Teamwork Award",
        "points_awarded": 100,
        "description": "Awarded for outstanding contribution to team spirit.",
        "giver_id": 1,
        "giver_username": "admin_user",
        "timestamp": "2025-11-24T15:30:00Z"
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to view award details.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Award with ID '101' not found.",
        "code": "AWARD_NOT_FOUND"
    }
    ```

## 4. DELETE /api/awards/<int:award_id>

Revokes and deletes a specific award from the platform.

*   **Description**: This endpoint allows an administrator to remove a previously granted award. Upon successful deletion, the points associated with this award will be deducted from the recipient user's score.
*   **Method**: `DELETE`
*   **URL**: `/api/awards/{award_id}`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Path Parameters**:
    *   `award_id` (integer, required): The unique ID of the award to delete.
*   **Example Request**:
    ```http
    DELETE /api/awards/101 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Response (Success - 204 No Content)**:
    *   No content is returned, indicating successful deletion.
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to delete awards.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Award with ID '101' not found.",
        "code": "AWARD_NOT_FOUND"
    }
    ```

## 5. GET /api/users/<int:user_id>/awards

Retrieves all awards granted to a specific user.

*   **Description**: Allows retrieval of all awards associated with a particular user ID. This endpoint can be accessed by administrators to view any user's awards, or by a non-admin user to view their *own* awards (if `user_id` matches their authenticated ID).
*   **Method**: `GET`
*   **URL**: `/api/users/{user_id}/awards`
*   **Authentication**: `X-API-KEY` header (required). Admin users can specify any `user_id`. Non-admin users must have their `user_id` match the authenticated API key's user ID.
*   **Path Parameters**:
    *   `user_id` (integer, required): The ID of the user whose awards are to be retrieved.
*   **Query Parameters**:
    *   `limit` (integer, optional): The maximum number of awards to return per page. Defaults to a platform-defined value.
    *   `offset` (integer, optional): The number of awards to skip before starting to collect the result set.
*   **Example Request (Admin user for any user_id)**:
    ```http
    GET /api/users/5/awards HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Request (Non-admin user for their own awards)**:
    ```http
    GET /api/users/5/awards HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_USER_API_KEY_FOR_USER_5
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "awards": [
            {
                "id": 101,
                "user_id": 5,
                "username": "award_recipient",
                "category_id": 2,
                "category_name": "Teamwork Award",
                "points_awarded": 100,
                "description": "Awarded for outstanding contribution to team spirit.",
                "giver_id": 1,
                "giver_username": "admin_user",
                "timestamp": "2025-11-24T15:30:00Z"
            },
            {
                "id": 102,
                "user_id": 5,
                "username": "award_recipient",
                "category_id": 1,
                "category_name": "First Blood",
                "points_awarded": 50,
                "description": "First solve of Web Challenge 1",
                "giver_id": 3,
                "giver_username": "another_admin",
                "timestamp": "2025-11-23T10:00:00Z"
            }
        ],
        "total_awards": 2,
        "limit": 10,
        "offset": 0
    }
    ```
*   **Example Response (Error - 403 Forbidden - Non-admin accessing other user's awards)**:
    ```json
    {
        "message": "Access denied. You can only view your own awards.",
        "code": "ACCESS_DENIED"
    }
    ```
*   **Example Response (Error - 404 Not Found - User)**:
    ```json
    {
        "message": "User with ID '5' not found.",
        "code": "USER_NOT_FOUND"
    }
    ```