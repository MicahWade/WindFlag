# Submission API Endpoints

This section details the API endpoints for retrieving challenge submissions in the WindFlag CTF Platform. These endpoints are primarily designed for administrative use, offering powerful tools for auditing user activity and analyzing challenge performance.

## Authentication

All endpoints within the Submission API namespace are privileged and require administrator authentication. Access is granted via a user-generated API key, which must correspond to an account with administrative permissions.

*   **Mechanism**: The API key must be securely transmitted in the `X-API-KEY` HTTP header for every request.
*   **Permissions**: Only API keys belonging to users with `is_admin: true` (or `is_super_admin: true`) privileges will be authorized to access these endpoints.
*   **Further Details**: For more comprehensive information on API key generation, management, and authentication protocols, please refer to the [API Overview](./api_overview.md) documentation.

## 1. GET /api/submissions

Retrieves a paginated and filterable list of all challenge submissions made across the platform.

*   **Description**: This endpoint provides a comprehensive audit log of every flag submission attempt. It's an essential tool for administrators to monitor user activity, investigate suspicious behavior, track challenge solve rates, and understand how users are interacting with the CTF challenges.
*   **Method**: `GET`
*   **URL**: `/api/submissions`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Query Parameters**:
    *   `user_id` (integer, optional): Filters submissions to include only those made by a specific user, identified by their numerical `id`.
    *   `username` (string, optional): Filters submissions by the username of the submitting user.
    *   `challenge_id` (integer, optional): Filters submissions to include only those for a specific challenge, identified by its numerical `id`.
    *   `challenge_name` (string, optional): Filters submissions by the name of the challenge.
    *   `is_correct` (boolean, optional): Filters submissions to show only correct (`true`) or incorrect (`false`) attempts.
    *   `start_time` (string, ISO 8601, optional): Filters submissions made after or at this UTC timestamp. Example: `2023-10-27T00:00:00Z`.
    *   `end_time` (string, ISO 8601, optional): Filters submissions made before or at this UTC timestamp. Example: `2023-10-27T23:59:59Z`.
    *   `limit` (integer, optional): The maximum number of submission records to return in a single response. Defaults to a platform-defined value (e.g., 20).
    *   `offset` (integer, optional): The number of submission records to skip from the beginning of the result set. Useful for pagination.
    *   `sort_by` (string, optional): Field to sort the results by. Common values include `timestamp`, `user_id`, `challenge_id`, `score_at_submission`. Defaults to `timestamp`.
    *   `sort_order` (string, optional): Sort order, either `asc` (ascending) or `desc` (descending). Defaults to `desc`.
*   **Example Request**:
    ```http
    GET /api/submissions?user_id=1&is_correct=true&sort_by=timestamp&sort_order=desc&limit=5 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "submissions": [
            {
                "id": 2,
                "user_id": 2,
                "username": "player_two",
                "challenge_id": 1,
                "challenge_name": "Warmup Challenge",
                "submitted_flag": "flag{test_flag_submitted}",
                "is_correct": true,
                "timestamp": "2023-10-27T10:05:00.000Z",
                "score_at_submission": 120
            },
            {
                "id": 1,
                "user_id": 1,
                "username": "player_one",
                "challenge_id": 1,
                "challenge_name": "Warmup Challenge",
                "submitted_flag": "flag{welcome_to_windflag}",
                "is_correct": true,
                "timestamp": "2023-10-27T10:00:00.000Z",
                "score_at_submission": 100
            }
        ],
        "total_submissions": 2,
        "limit": 5,
        "offset": 0
    }
    ```
    *   `id` (integer): The unique numerical identifier for the submission record.
    *   `user_id` (integer): The ID of the user who made the submission.
    *   `username` (string): The username of the user who made the submission.
    *   `challenge_id` (integer): The ID of the challenge to which the flag was submitted.
    *   `challenge_name` (string): The name of the challenge to which the flag was submitted.
    *   `submitted_flag` (string): The actual flag string submitted by the user. (Note: May be partially masked or omitted for highly sensitive flags for non-admin requests if this endpoint were exposed to non-admins).
    *   `is_correct` (boolean): `true` if the submitted flag was correct, `false` otherwise.
    *   `timestamp` (string, ISO 8601): The UTC timestamp when the flag was submitted.
    *   `score_at_submission` (integer): The user's total score at the exact moment this submission was made.
    *   `total_submissions` (integer): The total number of submissions matching the query parameters (useful for pagination).
    *   `limit` (integer): The `limit` applied to the query.
    *   `offset` (integer): The `offset` applied to the query.
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to view submissions.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 400 Bad Request)**:
    ```json
    {
        "message": "Invalid query parameter value for 'limit'. Must be a positive integer.",
        "code": "BAD_REQUEST_VALIDATION"
    }
    ```

## 2. GET /api/submissions/<int:submission_id>

Retrieves detailed information for a specific challenge submission.

*   **Description**: Fetches the full details of a single submission record given its unique identifier. This is useful for in-depth investigation of a particular submission.
*   **Method**: `GET`
*   **URL**: `/api/submissions/{submission_id}`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Path Parameters**:
    *   `submission_id` (integer, required): The unique ID of the submission to retrieve.
*   **Example Request**:
    ```http
    GET /api/submissions/2 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "id": 2,
        "user_id": 2,
        "username": "player_two",
        "challenge_id": 1,
        "challenge_name": "Warmup Challenge",
        "submitted_flag": "flag{test_flag_submitted}",
        "is_correct": true,
        "timestamp": "2023-10-27T10:05:00.000Z",
        "score_at_submission": 120
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to view submission details.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Submission with ID '2' not found.",
        "code": "SUBMISSION_NOT_FOUND"
    }
    ```

## 3. GET /api/users/<int:user_id>/submissions

Retrieves all challenge submissions made by a specific user.

*   **Description**: Returns a list of all submission records associated with a particular user ID. This endpoint can be accessed by administrators to view any user's submissions, or by a non-admin user to view their *own* submissions (if `user_id` matches their authenticated ID).
*   **Method**: `GET`
*   **URL**: `/api/users/{user_id}/submissions`
*   **Authentication**: `X-API-KEY` header (required). Admin users can specify any `user_id`. Non-admin users must have their `user_id` match the authenticated API key's user ID.
*   **Path Parameters**:
    *   `user_id` (integer, required): The ID of the user whose submissions are to be retrieved.
*   **Query Parameters**:
    *   `challenge_id` (integer, optional): Filters submissions by a specific challenge ID.
    *   `is_correct` (boolean, optional): Filters submissions to show only correct (`true`) or incorrect (`false`) attempts.
    *   `limit` (integer, optional): The maximum number of submissions to return per page.
    *   `offset` (integer, optional): The number of submissions to skip.
    *   `sort_by` (string, optional): Field to sort the results by.
    *   `sort_order` (string, optional): Sort order, `asc` or `desc`.
*   **Example Request (Admin user for any user_id)**:
    ```http
    GET /api/users/1/submissions HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Request (Non-admin user for their own submissions)**:
    ```http
    GET /api/users/1/submissions HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_USER_API_KEY_FOR_USER_1
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "submissions": [
            {
                "id": 1,
                "user_id": 1,
                "username": "player_one",
                "challenge_id": 1,
                "challenge_name": "Warmup Challenge",
                "submitted_flag": "flag{welcome_to_windflag}",
                "is_correct": true,
                "timestamp": "2023-10-27T10:00:00.000Z",
                "score_at_submission": 100
            },
            {
                "id": 3,
                "user_id": 1,
                "username": "player_one",
                "challenge_id": 2,
                "challenge_name": "Web Challenge 1",
                "submitted_flag": "flag{wrong_flag}",
                "is_correct": false,
                "timestamp": "2023-10-27T11:30:00.000Z",
                "score_at_submission": 100
            }
        ],
        "total_submissions": 2
    }
    ```
*   **Example Response (Error - 403 Forbidden - Non-admin accessing other user's submissions)**:
    ```json
    {
        "message": "Access denied. You can only view your own submissions.",
        "code": "ACCESS_DENIED"
    }
    ```
*   **Example Response (Error - 404 Not Found - User)**:
    ```json
    {
        "message": "User with ID '1' not found.",
        "code": "USER_NOT_FOUND"
    }
    ```

## 4. GET /api/challenges/<int:challenge_id>/submissions

Retrieves all submissions made for a specific challenge.

*   **Description**: Returns a list of all submission records associated with a particular challenge ID. This endpoint is primarily for administrators to analyze how users are attempting and solving a given challenge.
*   **Method**: `GET`
*   **URL**: `/api/challenges/{challenge_id}/submissions`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Path Parameters**:
    *   `challenge_id` (integer, required): The ID of the challenge whose submissions are to be retrieved.
*   **Query Parameters**:
    *   `user_id` (integer, optional): Filters submissions by a specific user ID.
    *   `is_correct` (boolean, optional): Filters submissions to show only correct (`true`) or incorrect (`false`) attempts.
    *   `limit` (integer, optional): The maximum number of submissions to return per page.
    *   `offset` (integer, optional): The number of submissions to skip.
    *   `sort_by` (string, optional): Field to sort the results by.
    *   `sort_order` (string, optional): Sort order, `asc` or `desc`.
*   **Example Request**:
    ```http
    GET /api/challenges/1/submissions HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "submissions": [
            {
                "id": 2,
                "user_id": 2,
                "username": "player_two",
                "challenge_id": 1,
                "challenge_name": "Warmup Challenge",
                "submitted_flag": "flag{test_flag_submitted}",
                "is_correct": true,
                "timestamp": "2023-10-27T10:05:00.000Z",
                "score_at_submission": 120
            },
            {
                "id": 1,
                "user_id": 1,
                "username": "player_one",
                "challenge_id": 1,
                "challenge_name": "Warmup Challenge",
                "submitted_flag": "flag{welcome_to_windflag}",
                "is_correct": true,
                "timestamp": "2023-10-27T10:00:00.000Z",
                "score_at_submission": 100
            }
        ],
        "total_submissions": 2
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to view challenge submissions.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 404 Not Found - Challenge)**:
    ```json
    {
        "message": "Challenge with ID '1' not found.",
        "code": "CHALLENGE_NOT_FOUND"
    }
    ```

## 5. DELETE /api/submissions/<int:submission_id>

Deletes a specific challenge submission record.

*   **Description**: Allows an administrator to remove a submission record. This action is irreversible and should be used with caution, primarily for correcting errors or removing fraudulent submissions. Note that deleting a submission does *not* automatically revert any score changes that occurred from that submission; manual score adjustment may be necessary if it was a correct submission.
*   **Method**: `DELETE`
*   **URL**: `/api/submissions/{submission_id}`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Path Parameters**:
    *   `submission_id` (integer, required): The unique ID of the submission record to delete.
*   **Example Request**:
    ```http
    DELETE /api/submissions/2 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Response (Success - 204 No Content)**:
    *   No content is returned, indicating successful deletion.
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to delete submissions.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Submission with ID '2' not found.",
        "code": "SUBMISSION_NOT_FOUND"
    }
    ```