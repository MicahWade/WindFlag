# Category API Endpoints

This section details the API endpoints for managing categories in the WindFlag CTF Platform. These endpoints allow administrators to programmatically create, retrieve, update, and delete challenge categories.

## Authentication

All endpoints in the Category API namespace require administrator authentication using a user-generated API key. This key must be provided in the `X-API-KEY` header for every request.

For more information on generating and managing API keys, please refer to the [API Overview](./api_overview.md).

## 1. POST /api/categories

Creates a new category.

*   **Description**: Allows an administrator to create a new category by providing its name in a JSON payload.
*   **Method**: `POST`
*   **URL**: `/api/categories`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Request Body**: `application/json`
    ```json
    {
        "name": "New API Category"
    }
    ```
*   **Example Response (Success - 201 Created)**:
    ```json
    {
        "message": "Category created successfully",
        "category": {
            "id": 5,
            "name": "New API Category"
        }
    }
    ```
*   **Example Response (Error - 400 Bad Request)**:
    ```json
    {
        "message": "Request body must be JSON and include a name"
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required"
    }
    ```

## 2. GET /api/categories

Retrieves a list of all categories.

*   **Description**: Returns an array of all categories with their basic information.
*   **Method**: `GET`
*   **URL**: `/api/categories`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Example Response (Success - 200 OK)**:
    ```json
    [
        {
            "id": 1,
            "name": "Category 1"
        },
        {
            "id": 2,
            "name": "Category 2"
        }
    ]
    ```

## 3. GET /api/categories/<int:category_id>

Retrieves details for a single category.

*   **Description**: Returns full details for a specific category identified by its ID.
*   **Method**: `GET`
*   **URL**: `/api/categories/<int:category_id>`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "id": 1,
        "name": "Category 1"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Not Found"
    }
    ```

## 4. PUT /api/categories/<int:category_id>

Updates an existing category.

*   **Description**: Modifies the details of a specific category. Only fields included in the JSON payload will be updated.
*   **Method**: `PUT`
*   **URL**: `/api/categories/<int:category_id>`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Request Body**: `application/json`
    ```json
    {
        "name": "Updated Category Name"
    }
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "message": "Category updated successfully"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Not Found"
    }
    ```

## 5. DELETE /api/categories/<int:category_id>

Deletes a category.

*   **Description**: Removes a specific category from the database.
*   **Method**: `DELETE`
*   **URL**: `/api/categories/<int:category_id>`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "message": "Category deleted successfully"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Not Found"
    }
    ```
