# Category API Endpoints

This section details the API endpoints for managing categories in the WindFlag CTF Platform. These endpoints allow administrators to programmatically create, retrieve, update, and delete challenge categories.

## Authentication

All endpoints in the Category API namespace require administrator authentication using a user-generated API key. This key must be provided in the `X-API-KEY` header for every request.

For more information on generating and managing API keys, please refer to the [API Overview](./api_overview.md).

# Category API Endpoints

This section details the API endpoints for managing challenge categories within the WindFlag CTF Platform. These endpoints allow administrators to programmatically create, retrieve, update, and delete challenge categories, enabling dynamic organization and progression of CTF challenges.

## Authentication

All endpoints within the Category API namespace are privileged and require administrator authentication. Access is granted via a user-generated API key, which must correspond to an account with administrative permissions.

*   **Mechanism**: The API key must be securely transmitted in the `X-API-KEY` HTTP header for every request.
*   **Permissions**: Only API keys belonging to users with `is_admin: true` (or `is_super_admin: true`) privileges will be authorized to access these endpoints.
*   **Further Details**: For more comprehensive information on API key generation, management, and authentication protocols, please refer to the [API Overview](./api_overview.md) documentation.

## 1. POST /api/categories

Creates a new challenge category.

*   **Description**: This endpoint allows an administrator to define and create a new category. The structure of this payload directly corresponds to the category definition detailed in the `docs/yaml.md` file, ensuring consistency for both programmatic and YAML-based category creation. Comprehensive validation is applied to all incoming data.
*   **Method**: `POST`
*   **URL**: `/api/categories`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Request Body**: `application/json`. The body should contain a JSON object representing the category.
    *   **`name`** (string, required): The unique name of the category. Must be unique across all categories.
    *   **`description`** (string, optional): A brief description for the category.
    *   **`unlock_type`** (string, optional): The type of unlocking mechanism. Defaults to `NONE`. Valid values: `NONE`, `PREREQUISITE_PERCENTAGE`, `PREREQUISITE_COUNT`, `PREREQUISITE_CHALLENGES`, `TIMED`, `COMBINED`. (Refer to `docs/yaml.md` for detailed explanations).
    *   **`prerequisite_percentage_value`** (integer, optional): Required if `unlock_type` is `PREREQUISITE_PERCENTAGE` or `COMBINED`. An integer between 1 and 100.
    *   **`prerequisite_count_value`** (integer, optional): Required if `unlock_type` is `PREREQUISITE_COUNT` or `COMBINED`. A positive integer representing the number of challenges to solve.
    *   **`prerequisite_count_category_ids`** (array of integers, optional): A list of category IDs. If provided with `PREREQUISITE_COUNT` or `COMBINED`, `prerequisite_count_value` applies only to challenges within these categories.
    *   **`prerequisite_challenge_ids`** (array of integers, optional): A list of challenge IDs. Required if `unlock_type` is `PREREQUISITE_CHALLENGES` or `COMBINED`.
    *   **`unlock_date_time`** (string, ISO 8601, optional): Required if `unlock_type` is `TIMED` or `COMBINED`. UTC datetime string (e.g., "YYYY-MM-DDTHH:MM:SSZ").
    *   **`is_hidden`** (boolean, optional): If `true`, the category is hidden from non-admin users until unlocked. Defaults to `false`.
*   **Example Request**:
    ```http
    POST /api/categories HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    Content-Type: application/json

    {
        "name": "Web Exploitation Advanced",
        "description": "More complex web challenges.",
        "unlock_type": "PREREQUISITE_PERCENTAGE",
        "prerequisite_percentage_value": 75,
        "is_hidden": true
    }
    ```
*   **Example Response (Success - 201 Created)**:
    ```json
    {
        "message": "Category created successfully",
        "category": {
            "id": 5,
            "name": "Web Exploitation Advanced",
            "unlock_type": "PREREQUISITE_PERCENTAGE",
            "is_hidden": true
        }
    }
    ```
    *   `message`: Confirmation message.
    *   `category`: A partial object of the newly created category, including its `id`, `name`, `unlock_type`, and `is_hidden`.
*   **Example Response (Error - 400 Bad Request - Missing Fields)**:
    ```json
    {
        "message": "Missing required field: name.",
        "code": "BAD_REQUEST_MISSING_FIELD"
    }
    ```
*   **Example Response (Error - 400 Bad Request - Invalid Data)**:
    ```json
    {
        "message": "Validation error: Prerequisite percentage value must be between 1 and 100.",
        "code": "BAD_REQUEST_VALIDATION"
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to create categories.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 409 Conflict)**:
    ```json
    {
        "message": "Category with name 'Web Exploitation Advanced' already exists.",
        "code": "CATEGORY_NAME_CONFLICT"
    }
    ```

## 2. GET /api/categories

Retrieves a paginated and filterable list of all categories.

*   **Description**: Returns an array of category objects, allowing for flexible retrieval of category information. Administrators can view all categories, including hidden ones, while regular users will only see categories that are visible and unlocked for them. The response can be filtered, sorted, and paginated.
*   **Method**: `GET`
*   **URL**: `/api/categories`
*   **Authentication**: `X-API-KEY` header (required). Admin users will see all categories; regular users will see categories based on their visibility and unlock status.
*   **Query Parameters**:
    *   `name_search` (string, optional): Performs a partial, case-insensitive search on category names.
    *   `is_hidden` (boolean as "true"/"false", optional): *Admin only*. Filters categories by their hidden status.
    *   `unlocked_for_user_id` (integer, optional): Filters categories that are unlocked for a specific user ID. *Admin only*.
    *   `unlock_type` (string, optional): Filters categories by their unlock type (e.g., `TIMED`, `PREREQUISITE_COUNT`).
    *   `limit` (integer, optional): The maximum number of categories to return per page. Defaults to a platform-defined value.
    *   `offset` (integer, optional): The number of categories to skip from the beginning of the result set. Useful for pagination.
    *   `sort_by` (string, optional): Field to sort the results by. Common values include `name`, `id`. Defaults to `name`.
    *   `sort_order` (string, optional): Sort order, either `asc` (ascending) or `desc` (descending). Defaults to `asc`.
*   **Example Request (Admin user, filter by name and hidden status)**:
    ```http
    GET /api/categories?name_search=Web&is_hidden=true HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Request (Regular user, get first 5 categories)**:
    ```http
    GET /api/categories?limit=5 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_USER_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "categories": [
            {
                "id": 1,
                "name": "Web Exploitation",
                "description": "Challenges related to web vulnerabilities.",
                "unlock_type": "NONE",
                "is_hidden": false,
                "is_unlocked": true, // Contextual for the authenticated user
                "challenge_count": 10 // Number of challenges in this category
            },
            {
                "id": 5,
                "name": "Web Exploitation Advanced",
                "description": "More complex web challenges.",
                "unlock_type": "PREREQUISITE_PERCENTAGE",
                "prerequisite_percentage_value": 75,
                "is_hidden": true,
                "is_unlocked": false,
                "challenge_count": 5
            }
        ],
        "total_categories": 2,
        "limit": 5,
        "offset": 0
    }
    ```
    *   Each object in the `categories` array provides summary information about a category.
    *   `is_unlocked` is context-dependent for the authenticated user.
*   **Example Response (Error - 400 Bad Request)**:
    ```json
    {
        "message": "Invalid value for 'limit'. Must be a positive integer.",
        "code": "BAD_REQUEST_VALIDATION"
    }
    ```
*   **Example Response (Error - 403 Forbidden - Non-admin trying to use admin-only filters)**:
    ```json
    {
        "message": "Access denied. 'is_hidden' filter is for administrators only.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```

## 3. GET /api/categories/<int:category_id>

Retrieves full details for a single category.

*   **Description**: This endpoint provides a comprehensive view of a specific category, identified by its unique ID. It includes all configuration details, such as unlock conditions and visibility status, along with the count of challenges within it.
*   **Method**: `GET`
*   **URL**: `/api/categories/{category_id}`
*   **Authentication**: `X-API-KEY` header (required). Admin users can retrieve details for any category. Regular users can only retrieve details for categories that are visible and unlocked for them.
*   **Path Parameters**:
    *   `category_id` (integer, required): The unique ID of the category to retrieve.
*   **Example Request**:
    ```http
    GET /api/categories/5 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_USER_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "id": 5,
        "name": "Web Exploitation Advanced",
        "description": "More complex web challenges.",
        "unlock_type": "PREREQUISITE_PERCENTAGE",
        "prerequisite_percentage_value": 75,
        "prerequisite_count_value": null,
        "prerequisite_count_category_ids": [],
        "prerequisite_challenge_ids": [],
        "unlock_date_time": null,
        "is_hidden": true,
        "is_unlocked": false, // Contextual for the authenticated user
        "prerequisites_met": false, // Contextual for the authenticated user
        "challenge_count": 5,
        "created_at": "2025-11-24T10:00:00Z",
        "updated_at": "2025-11-24T11:00:00Z"
    }
    ```
    *   **`id`** (integer): Unique identifier for the category.
    *   **`name`** (string): Name of the category.
    *   **`description`** (string, null): Description of the category.
    *   **`unlock_type`** (string): The type of unlocking mechanism (e.g., "NONE", "PREREQUISITE_PERCENTAGE").
    *   **`prerequisite_percentage_value`** (integer, null): The percentage required if `unlock_type` is `PREREQUISITE_PERCENTAGE` or `COMBINED`.
    *   **`prerequisite_count_value`** (integer, null): The count required if `unlock_type` is `PREREQUISITE_COUNT` or `COMBINED`.
    *   **`prerequisite_count_category_ids`** (array of integers): IDs of categories to count challenges from for `PREREQUISITE_COUNT`.
    *   **`prerequisite_challenge_ids`** (array of integers): IDs of challenges required if `unlock_type` is `PREREQUISITE_CHALLENGES` or `COMBINED`.
    *   **`unlock_date_time`** (string, ISO 8601, null): UTC timestamp for timed unlock.
    *   **`is_hidden`** (boolean): Whether the category is hidden from non-admins.
    *   **`is_unlocked`** (boolean): `true` if the authenticated user can currently access this category.
    *   **`prerequisites_met`** (boolean): `true` if the authenticated user has met all prerequisites for this category.
    *   **`challenge_count`** (integer): The number of challenges currently assigned to this category.
    *   **`created_at`** (string, ISO 8601): UTC timestamp when the category was created.
    *   **`updated_at`** (string, ISO 8601): UTC timestamp when the category was last updated.
*   **Example Response (Error - 401 Unauthorized)**:
    ```json
    {
        "message": "Invalid or inactive API Key. Authentication required.",
        "code": "AUTH_REQUIRED"
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Access denied. Category not unlocked for this user.",
        "code": "CATEGORY_LOCKED"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Category with ID '999' not found.",
        "code": "CATEGORY_NOT_FOUND"
    }
    ```

## 4. PUT /api/categories/<int:category_id>

Updates an existing category with new information.

*   **Description**: This endpoint allows administrators to modify the details of a specific category identified by its ID. It supports partial updates; only the fields included in the JSON payload will be updated. This flexibility enables granular changes without requiring a full re-submission of all category data.
*   **Method**: `PUT`
*   **URL**: `/api/categories/{category_id}`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Path Parameters**:
    *   `category_id` (integer, required): The unique ID of the category to update.
*   **Request Body**: `application/json`. The body should contain a JSON object with the fields to update. All fields listed under `POST /api/categories` can be used here, but only those provided will be modified.
    *   **Updatable Fields**:
        *   **`name`** (string, optional): Updates the category's name. Must remain unique.
        *   **`description`** (string, optional): Updates the category's description.
        *   **`unlock_type`** (string, optional): Changes the unlocking mechanism. Must be a valid type (`NONE`, `PREREQUISITE_PERCENTAGE`, `PREREQUISITE_COUNT`, `PREREQUISITE_CHALLENGES`, `TIMED`, `COMBINED`).
        *   **`prerequisite_percentage_value`** (integer, optional): Updates the required percentage for `PREREQUISITE_PERCENTAGE` or `COMBINED` types.
        *   **`prerequisite_count_value`** (integer, optional): Updates the required count for `PREREQUISITE_COUNT` or `COMBINED` types.
        *   **`prerequisite_count_category_ids`** (array of integers, optional): Updates the list of category IDs for counting prerequisites.
        *   **`prerequisite_challenge_ids`** (array of integers, optional): Updates the list of challenge IDs required for prerequisites.
        *   **`unlock_date_time`** (string, ISO 8601, optional): Updates the timed unlock timestamp.
        *   **`is_hidden`** (boolean, optional): Updates the category's hidden status.
*   **Example Request (Update name and description)**:
    ```http
    PUT /api/categories/5 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    Content-Type: application/json

    {
        "name": "Advanced Web Exploitation Techniques",
        "description": "Exploiting modern web applications."
    }
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "message": "Category updated successfully",
        "category_id": 5,
        "name": "Advanced Web Exploitation Techniques"
    }
    ```
    *   `message`: Confirmation message.
    *   `category_id`: The ID of the updated category.
    *   `name`: The new name of the category.
*   **Example Response (Error - 400 Bad Request - Invalid Data)**:
    ```json
    {
        "message": "Validation error: Invalid unlock type provided.",
        "code": "BAD_REQUEST_VALIDATION"
    }
    ```
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to update categories.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Category with ID '999' not found.",
        "code": "CATEGORY_NOT_FOUND"
    }
    ```
*   **Example Response (Error - 409 Conflict)**:
    ```json
    {
        "message": "Category with name 'Another existing category name' already exists.",
        "code": "CATEGORY_NAME_CONFLICT"
    }
    ```

## 5. DELETE /api/categories/<int:category_id>

Deletes a specific category from the platform.

*   **Description**: This endpoint allows an administrator to permanently remove a category identified by its unique ID. This is a destructive operation that requires careful consideration due to its impact on associated challenges.
    *   **Impact on Challenges**: Challenges previously belonging to the deleted category will become "Uncategorized." This means they will still exist but will no longer be associated with any specific category. Administrators may then need to manually reassign these challenges to another category or delete them if they are no longer needed.
    *   **Caution**: This action is irreversible.
*   **Method**: `DELETE`
*   **URL**: `/api/categories/{category_id}`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Path Parameters**:
    *   `category_id` (integer, required): The unique ID of the category to delete.
*   **Example Request**:
    ```http
    DELETE /api/categories/5 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Response (Success - 204 No Content)**:
    *   No content is returned in the response body, indicating successful deletion.
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to delete categories.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Category with ID '999' not found.",
        "code": "CATEGORY_NOT_FOUND"
    }
    ```
