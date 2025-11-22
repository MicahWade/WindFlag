# User API Endpoints (Admin Only)

This section details the API endpoints for managing users in the WindFlag CTF Platform. These endpoints allow administrators to programmatically retrieve and update user information.

## Authentication

All endpoints in the User API namespace require administrator authentication using a user-generated API key. This key must be provided in the `X-API-KEY` header for every request.

For more information on generating and managing API keys, please refer to the [API Overview](./api_overview.md).

## 1. GET /api/users

Retrieves a list of all users.

*   **Description**: Returns an array of all users with their basic information. This endpoint is for administrative purposes.
*   **Method**: `GET`
*   **URL**: `/api/users`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Example Response (Success - 200 OK)**:
    ```json
    [
        {
            "id": 1,
            "username": "admin1",
            "email": "admin1@example.com",
            "is_admin": true,
            "is_hidden": false
        },
        {
            "id": 2,
            "username": "user1",
            "email": "user1@example.com",
            "is_admin": false,
            "is_hidden": false
        }
    ]
    ```

## 2. GET /api/users/<int:user_id>

Retrieves details for a single user.

*   **Description**: Returns basic details for a specific user identified by their ID. This endpoint is for administrative purposes.
*   **Method**: `GET`
*   **URL**: `/api/users/<int:user_id>`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "id": 1,
        "username": "admin1",
        "email": "admin1@example.com",
        "is_admin": true,
        "is_hidden": false
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Not Found"
    }
    ```

## 3. PUT /api/users/<int:user_id>

Updates an existing user's status.

*   **Description**: Modifies the `is_hidden` or `is_admin` status of a specific user. Only fields included in the JSON payload will be updated.
*   **Method**: `PUT`
*   **URL**: `/api/users/<int:user_id>`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Request Body**: `application/json`
    ```json
    {
        "is_hidden": true,
        "is_admin": false
    }
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "message": "User updated successfully"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Not Found"
    }
    ```
