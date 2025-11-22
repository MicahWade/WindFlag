# Core API Endpoints

This section details the core endpoints of the WindFlag CTF Platform API. These endpoints provide general status checks and user-specific information.

## Authentication

All endpoints in the Core API namespace require authentication using a user-generated API key. This key must be provided in the `X-API-KEY` header for every request.

For more information on generating and managing API keys, please refer to the [API Overview](../api_overview.md) and the platform's user interface.

## 1. GET /status

Checks the API server's status and verifies API key authentication.

*   **Description**: A simple endpoint to confirm that the API is operational and that the provided API key is valid and active.
*   **Method**: `GET`
*   **URL**: `/api/v1/status`
*   **Authentication**: `X-API-KEY` header (required)
*   **Example Request**:
    ```http
    GET /api/v1/status HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_USER_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "message": "API key authenticated successfully!",
        "user": "authenticated_username"
    }
    ```
*   **Example Response (Error - 401 Unauthorized - Missing Key)**:
    ```json
    {
        "message": "API Key is missing"
    }
    ```
*   **Example Response (Error - 401 Unauthorized - Invalid Key)**:
    ```json
    {
        "message": "Invalid or inactive API Key"
    }
    ```

## 2. GET /users/me

Retrieves the profile information for the authenticated user.

*   **Description**: Returns detailed profile information for the user associated with the provided API key.
*   **Method**: `GET`
*   **URL**: `/api/v1/users/me`
*   **Authentication**: `X-API-KEY` header (required)
*   **Example Request**:
    ```http
    GET /api/v1/users/me HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_USER_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "id": 1,
        "username": "authenticated_username",
        "email": "user@example.com",
        "score": 1200,
        "is_admin": false,
        "last_seen": "2023-10-26T14:30:00.000Z"
    }
    ```
*   **Example Response (Error - 401 Unauthorized)**:
    ```json
    {
        "message": "Invalid or inactive API Key"
    }
    ```
