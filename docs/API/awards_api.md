# Award API Endpoints

This section details the API endpoints for managing awards given to users in the WindFlag CTF Platform. These endpoints allow administrators to programmatically give awards to users.

## Authentication

All endpoints in the Award API namespace require administrator authentication using a user-generated API key. This key must be provided in the `X-API-KEY` header for every request.

For more information on generating and managing API keys, please refer to the [API Overview](./api_overview.md).

## 1. POST /api/awards

Gives an award to a user.

*   **Description**: Allows an administrator to give an award to a specific user, assigning points based on an award category.
*   **Method**: `POST`
*   **URL**: `/api/awards`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Request Body**: `application/json`
    ```json
    {
        "user_id": 1,
        "category_id": 1,
        "points_awarded": 50
    }
    ```
*   **Example Response (Success - 201 Created)**:
    ```json
    {
        "message": "Award given successfully",
        "award": {
            "id": 1,
            "user_id": 1,
            "category_id": 1,
            "points_awarded": 50
        }
    }
    ```
*   **Example Response (Error - 400 Bad Request)**:
    ```json
    {
        "message": "Request body must be JSON and include user_id, category_id, and points_awarded"
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Not Found"
    }
    ```
