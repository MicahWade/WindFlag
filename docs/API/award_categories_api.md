# Award Category API Endpoints

This section details the API endpoints for managing award categories in the WindFlag CTF Platform. These endpoints allow administrators to programmatically create, retrieve, update, and delete award categories.

## Authentication

All endpoints in the Award Category API namespace require administrator authentication using a user-generated API key. This key must be provided in the `X-API-KEY` header for every request.

For more information on generating and managing API keys, please refer to the [API Overview](./api_overview.md).

## 1. POST /api/award_categories

Creates a new award category.

*   **Description**: Allows an administrator to create a new award category by providing its name and default points in a JSON payload.
*   **Method**: `POST`
*   **URL**: `/api/award_categories`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Request Body**: `application/json`
    ```json
    {
        "name": "New Award Category",
        "default_points": 50
    }
    ```
*   **Example Response (Success - 201 Created)**:
    ```json
    {
        "message": "Award category created successfully",
        "award_category": {
            "id": 1,
            "name": "New Award Category",
            "default_points": 50
        }
    ```
*   **Example Response (Error - 400 Bad Request)**:
    ```json
    {
        "message": "Request body must be JSON and include name and default_points"
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required"
    }
    ```

## 2. GET /api/award_categories

Retrieves a list of all award categories.

*   **Description**: Returns an array of all award categories with their basic information.
*   **Method**: `GET`
*   **URL**: `/api/award_categories`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Example Response (Success - 200 OK)**:
    ```json
    [
        {
            "id": 1,
            "name": "Bug Report",
            "default_points": 50
        },
        {
            "id": 2,
            "name": "Feature Suggestion",
            "default_points": 30
        }
    ]
    ```

## 3. GET /api/award_categories/<int:category_id>

Retrieves details for a single award category.

*   **Description**: Returns full details for a specific award category identified by its ID.
*   **Method**: `GET`
*   **URL**: `/api/award_categories/<int:category_id>`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "id": 1,
        "name": "Bug Report",
        "default_points": 50
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Not Found"
    }
    ```

## 4. PUT /api/award_categories/<int:category_id>

Updates an existing award category.

*   **Description**: Modifies the details of a specific award category. Only fields included in the JSON payload will be updated.
*   **Method**: `PUT`
*   **URL**: `/api/award_categories/<int:category_id>`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Request Body**: `application/json`
    ```json
    {
        "name": "Updated Bug Report Category",
        "default_points": 60
    }
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "message": "Award category updated successfully"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Not Found"
    }
    ```

## 5. DELETE /api/award_categories/<int:category_id>

Deletes an award category.

*   **Description**: Removes a specific award category from the database.
*   **Method**: `DELETE`
*   **URL**: `/api/award_categories/<int:category_id>`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "message": "Award category deleted successfully"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Not Found"
    }
    ```
*   **Example Response (Error - 400 Bad Request)**:
    ```json
    {
        "message": "Cannot delete category with associated awards. Please delete awards first."
    }
    ```
