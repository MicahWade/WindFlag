# Settings API Endpoints

This section details the API endpoints for managing application-wide settings in the WindFlag CTF Platform. These endpoints allow administrators to programmatically retrieve and update settings.

## Authentication

All endpoints in the Settings API namespace require administrator authentication using a user-generated API key. This key must be provided in the `X-API-KEY` header for every request.

For more information on generating and managing API keys, please refer to the [API Overview](./api_overview.md).

## 1. GET /api/settings

Retrieves all application settings.

*   **Description**: Returns an array of all application settings as key-value pairs.
*   **Method**: `GET`
*   **URL**: `/api/settings`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Example Response (Success - 200 OK)**:
    ```json
    [
        {
            "key": "TOP_X_SCOREBOARD",
            "value": "10"
        },
        {
            "key": "SCOREBOARD_GRAPH_TYPE",
            "value": "line"
        }
    ]
    ```

## 2. PUT /api/settings

Updates an application setting.

*   **Description**: Modifies the value of a specific application setting. If the setting key does not exist, it will be created.
*   **Method**: `PUT`
*   **URL**: `/api/settings`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Request Body**: `application/json`
    ```json
    {
        "key": "TOP_X_SCOREBOARD",
        "value": "20"
    }
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "message": "Setting updated successfully"
    }
    ```
*   **Example Response (Error - 400 Bad Request)**:
    ```json
    {
        "message": "Request body must be JSON and include key and value"
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required"
    }
    ```
