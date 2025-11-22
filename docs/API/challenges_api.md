# Challenge API Endpoints

This section details the API endpoints for managing challenges in the WindFlag CTF Platform. These endpoints allow administrators to programmatically create, retrieve, update, and delete challenges.

## Authentication

All endpoints in the Challenge API namespace require administrator authentication using a user-generated API key. This key must be provided in the `X-API-KEY` header for every request.

For more information on generating and managing API keys, please refer to the [API Overview](./api_overview.md).

## 1. POST /api/challenges

Creates a new challenge.

*   **Description**: Allows an administrator to create a new challenge by providing its details in a JSON payload.
*   **Method**: `POST`
*   **URL**: `/api/challenges`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Request Body**: `application/json`
    ```json
    {
        "name": "New API Challenge",
        "description": "This challenge was created via the API.",
        "points": 100,
        "category_id": 1,
        "case_sensitive": true,
        "multi_flag_type": "SINGLE",
        "flags": ["flag{api_challenge_flag}"]
        // ... other challenge fields (multi_flag_threshold, point_decay_type, etc.)
    }
    ```
*   **Example Response (Success - 201 Created)**:
    ```json
    {
        "message": "Challenge created successfully",
        "challenge": {
            "id": 101,
            "name": "New API Challenge"
        }
    }
    ```
*   **Example Response (Error - 400 Bad Request)**:
    ```json
    {
        "message": "Missing required fields"
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required"
    }
    ```

## 2. GET /api/challenges

Retrieves a list of all challenges.

*   **Description**: Returns an array of all challenges with their basic information.
*   **Method**: `GET`
*   **URL**: `/api/challenges`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Example Request**:
    ```bash
    curl -X GET \\
      http://127.0.0.1:5001/api/challenges \\
      -H 'X-API-KEY: YOUR_ADMIN_API_KEY'
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    [
        {
            "id": 1,
            "name": "Challenge 1",
            "points": 100
        },
        {
            "id": 2,
            "name": "Challenge 2",
            "points": 150
        }
    ]
    ```

## 3. GET /api/challenges/<int:challenge_id>

Retrieves details for a single challenge.

*   **Description**: Returns full details for a specific challenge identified by its ID.
*   **Method**: `GET`
*   **URL**: `/api/challenges/<int:challenge_id>`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "id": 1,
        "name": "Challenge 1",
        "description": "Description for challenge 1",
        "points": 100,
        "category_id": 1,
        "case_sensitive": true,
        "multi_flag_type": "SINGLE",
        "multi_flag_threshold": null,
        "flags": [
            {"id": 1, "content": "flag{challenge1_flag}"}
        ]
        // ... other challenge fields
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Not Found"
    }
    ```

## 4. PUT /api/challenges/<int:challenge_id>

Updates an existing challenge.

*   **Description**: Modifies the details of a specific challenge. Only fields included in the JSON payload will be updated. Flags can be entirely replaced by providing a new `flags` array.
*   **Method**: `PUT`
*   **URL**: `/api/challenges/<int:challenge_id>`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Request Body**: `application/json`
    ```json
    {
        "description": "Updated description for API challenge.",
        "points": 120,
        "flags": ["flag{updated_api_flag_1}", "flag{updated_api_flag_2}"]
    }
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "message": "Challenge updated successfully"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Not Found"
    }
    ```

## 5. DELETE /api/challenges/<int:challenge_id>

Deletes a challenge.

*   **Description**: Removes a specific challenge and its associated flags and submissions from the database.
*   **Method**: `DELETE`
*   **URL**: `/api/challenges/<int:challenge_id>`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "message": "Challenge deleted successfully"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Not Found"
    }
    ```
