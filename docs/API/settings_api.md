# Settings API Endpoints

This section details the API endpoints for managing application-wide settings in the WindFlag CTF Platform. These endpoints provide administrators with the capability to programmatically retrieve, update, and manage various configuration parameters that control the behavior and appearance of the entire CTF instance.

## Authentication

All endpoints within the Settings API namespace are privileged and require administrator authentication. Access is granted via a user-generated API key, which must correspond to an account with administrative permissions.

*   **Mechanism**: The API key must be securely transmitted in the `X-API-KEY` HTTP header for every request.
*   **Permissions**: Only API keys belonging to users with `is_admin: true` (or `is_super_admin: true`) privileges will be authorized to access these endpoints.
*   **Further Details**: For more comprehensive information on API key generation, management, and authentication protocols, please refer to the [API Overview](./api_overview.md) documentation.

## 1. GET /api/settings

Retrieves all application settings configured within the platform.

*   **Description**: This endpoint provides a comprehensive list of all stored application settings, returned as an array of key-value pairs. It's an invaluable resource for administrators to review the current configuration of the CTF platform. The settings retrieved via this endpoint reflect the current state of the application's configurable parameters.
*   **Method**: `GET`
*   **URL**: `/api/settings`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Example Response (Success - 200 OK)**:
    ```json
    [
        {
            "key": "APP_NAME",
            "value": "WindFlag CTF"
        },
        {
            "key": "REQUIRE_JOIN_CODE",
            "value": "true"
        },
        {
            "key": "JOIN_CODE",
            "value": "SECURECODE123"
        },
        {
            "key": "DISABLE_SIGNUP",
            "value": "false"
        },
        {
            "key": "SCOREBOARD_FREEZE",
            "value": "false"
        },
        {
            "key": "SCOREBOARD_GRAPH_TYPE",
            "value": "line"
        },
        {
            "key": "FLAG_SUBMISSION_COOLDOWN_SECONDS",
            "value": "5"
        },
        {
            "key": "ANNOUNCEMENT_BANNER_MESSAGE",
            "value": "Welcome to the CTF! Good luck!"
        },
        {
            "key": "DEFAULT_THEME",
            "value": "cyberdeck"
        }
    ]
    ```
    *   Each object in the array represents a single application setting.
    *   **`key`** (string): The unique identifier for the setting (e.g., `APP_NAME`, `JOIN_CODE`).
    *   **`value`** (string): The current value associated with the setting. Note that all values are returned as strings, and the client application should handle type conversion (e.g., "true" to boolean `true`, "10" to integer `10`).
    *   **Common Setting Keys and Expected Value Types**:
        *   `APP_NAME`: (string) The name of the CTF platform.
        *   `SECRET_KEY`: (string) *Not exposed via API for security reasons.*
        *   `REQUIRE_JOIN_CODE`: (boolean as "true"/"false") Whether new user registration requires a join code.
        *   `JOIN_CODE`: (string) The actual join code if required.
        *   `DISABLE_SIGNUP`: (boolean as "true"/"false") Whether new user registrations are enabled.
        *   `REQUIRE_EMAIL`: (boolean as "true"/"false") Whether email is a required field for registration.
        *   `BASIC_INDEX_PAGE`: (boolean as "true"/"false") Controls the home page layout.
        *   `SCOREBOARD_FREEZE`: (boolean as "true"/"false") Whether the scoreboard is frozen.
        *   `SCOREBOARD_GRAPH_TYPE`: (string) Type of graph for the scoreboard (e.g., "line", "bar").
        *   `FLAG_SUBMISSION_COOLDOWN_SECONDS`: (integer as string) Cooldown period between flag submissions.
        *   `ANNOUNCEMENT_BANNER_MESSAGE`: (string) Global announcement message displayed on a banner.
        *   `DEFAULT_THEME`: (string) The name of the active theme for the platform.
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to view application settings.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```

## 2. GET /api/settings/<string:key>

Retrieves the value of a specific application setting by its key.

*   **Description**: This endpoint allows for fetching the value of a single, named application setting. It's useful when an integration only needs to query a particular configuration parameter without retrieving all settings.
*   **Method**: `GET`
*   **URL**: `/api/settings/{key}`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Path Parameters**:
    *   `key` (string, required): The key of the setting to retrieve (e.g., `APP_NAME`).
*   **Example Request**:
    ```http
    GET /api/settings/DEFAULT_THEME HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "key": "DEFAULT_THEME",
        "value": "cyberdeck"
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to view application settings.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Setting with key 'NON_EXISTENT_SETTING' not found.",
        "code": "SETTING_NOT_FOUND"
    }
    ```

## 3. PUT /api/settings

Updates an existing application setting or creates a new one if the key does not already exist.

*   **Description**: This endpoint allows administrators to modify the value of an existing application setting. Crucially, if the provided `key` does not correspond to an existing setting, a new setting will be created with the specified `key` and `value`. This provides flexibility for dynamic configuration. Input values are subject to validation based on the expected type and format for each setting.
*   **Method**: `PUT`
*   **URL**: `/api/settings`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Request Body**: `application/json`
    *   **`key`** (string, required): The unique identifier of the setting to be updated or created.
    *   **`value`** (string, required): The new value for the setting. This value will be stored as a string, but the application will attempt to convert it to its appropriate type (e.g., boolean, integer) when the setting is used.
*   **Example Request (Update existing setting)**:
    ```http
    PUT /api/settings HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    Content-Type: application/json

    {
        "key": "TOP_X_SCOREBOARD",
        "value": "20"
    }
    ```
*   **Example Request (Create new setting)**:
    ```http
    PUT /api/settings HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    Content-Type: application/json

    {
        "key": "NEW_CUSTOM_SETTING",
        "value": "This is a custom message"
    }
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "message": "Setting 'TOP_X_SCOREBOARD' updated successfully"
    }
    ```
    *   `message`: A confirmation indicating which setting was updated or created.
*   **Example Response (Error - 400 Bad Request - Missing fields)**:
    ```json
    {
        "message": "Request body must be JSON and include 'key' and 'value'.",
        "code": "BAD_REQUEST_MISSING_FIELDS"
    }
    ```
*   **Example Response (Error - 400 Bad Request - Invalid value)**:
    ```json
    {
        "message": "Invalid value for setting 'FLAG_SUBMISSION_COOLDOWN_SECONDS'. Must be a positive integer.",
        "code": "BAD_REQUEST_VALIDATION"
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to update application settings.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```

## 4. DELETE /api/settings/<string:key>

Deletes a specific application setting.

*   **Description**: This endpoint allows an administrator to remove an existing application setting by its key. This action should be performed with caution, as deleting critical settings can impact application behavior.
*   **Method**: `DELETE`
*   **URL**: `/api/settings/{key}`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Path Parameters**:
    *   `key` (string, required): The key of the setting to delete.
*   **Example Request**:
    ```http
    DELETE /api/settings/NEW_CUSTOM_SETTING HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Response (Success - 204 No Content)**:
    *   No content is returned, indicating successful deletion.
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to delete application settings.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Setting with key 'NON_EXISTENT_SETTING' not found.",
        "code": "SETTING_NOT_FOUND"
    }
    ```