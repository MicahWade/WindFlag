# API Overview

This document provides an overview of the WindFlag CTF Platform API.

## Authentication

Access to the WindFlag CTF Platform API is secured using a robust API Key mechanism. This ensures that only authorized applications and users can interact with the platform's data and functionalities. To successfully make authenticated API requests, you must adhere to the following steps and best practices:

1.  **Generate an API Key**:
    *   **For Users**: Each individual user can generate their own API key from their user profile page within the WindFlag web interface. This key grants access to user-specific data and actions.
    *   **For Administrators**: Administrators, especially those needing to manage challenges, users, or settings programmatically, can generate API keys from the Admin Panel. These keys typically have broader permissions.
    *   **Process**: Navigate to your profile or the Admin API Key management section, and click on the "Generate API Key" button. **Important**: Copy your API key immediately upon generation, as it will often only be displayed once for security reasons. If lost, you will need to revoke it and generate a new one.

2.  **Include Your API Key in Requests**:
    *   For all authenticated API requests, you must include your generated API Key in the `X-API-KEY` HTTP header. The API will validate this key to authorize your request.
    *   **Example HTTP Header**:
        ```
        X-API-KEY: your_unique_and_secret_api_key_here
        ```
    *   **Failure to include or provide a valid API key will result in a `401 Unauthorized` or `403 Forbidden` response.**

### API Key Security and Best Practices

API keys are powerful credentials. Treat them with the same level of security as you would a password.

*   **Keep Keys Confidential**: Never hardcode API keys directly into your client-side code, public repositories, or easily accessible files.
*   **Use Environment Variables**: Store API keys as environment variables in your application's deployment environment.
*   **Server-Side Usage**: Always use API keys on your server-side applications where they cannot be exposed to end-users.
*   **Rotation**: Periodically revoke old API keys and generate new ones, especially if there's any suspicion of compromise.
*   **Least Privilege**: Generate API keys with the minimum necessary permissions required for the task at hand. For instance, a key for a public scoreboard display shouldn't have administrative write access.

## Endpoints

The WindFlag API is organized into several domain-specific endpoints, each addressing a particular aspect of the CTF platform. For comprehensive details, including request/response schemas, parameters, and examples, please refer to the dedicated documentation for each endpoint.

*   **[Core API Endpoints](core_api.md)**: Provides foundational API functionalities, including checking API status, retrieving current user profile information, and managing user-specific API keys. Essential for basic platform interaction.
*   **[Challenges API Endpoints](challenges_api.md)**: Offers a full suite of operations for challenges, including listing all available challenges, retrieving details for a specific challenge, and submitting flags. Administrators can also create, update, and delete challenges.
*   **[Category API Endpoints](categories_api.md)**: Dedicated to managing challenge categories. This includes listing existing categories, retrieving details for a particular category, and for administrators, creating, updating, and deleting categories with their respective unlock conditions.
*   **[User API Endpoints](users_api.md)**: Primarily for administrators, these endpoints facilitate comprehensive user management, such as listing all users, retrieving individual user profiles, creating new users, editing user details (e.g., roles, hidden status), and deleting user accounts. Non-admin users can access their own profile.
*   **[Award Category API Endpoints](award_categories_api.md)**: Allows administrators to manage the different types of award categories within the platform (e.g., "First Blood", "Participation"). This includes creating, listing, updating, and deleting award categories.
*   **[Award API Endpoints](awards_api.md)**: Provides functionality for administrators to grant specific awards to users, manage award details, and retrieve lists of awarded items. This enables recognition of achievements beyond points.
*   **[Settings API Endpoints](settings_api.md)**: Grants administrators programmatic access to view and modify global application settings, suchs as `APP_NAME`, `REQUIRE_JOIN_CODE`, and other configurable parameters.
*   **[Submission API Endpoints](submissions_api.md)**: Enables retrieval of all challenge submissions made on the platform. This is primarily an administrative feature for auditing and analysis of user activity.
*   **[Analytics API Endpoints](analytics_api.md)**: Offers access to various statistical and analytical data points, such as challenge solve rates, user score distributions, and other metrics to monitor CTF progress and performance.

For interactive API documentation with request/response schemas, please refer to the live documentation available at `/api/docs`. This provides a dynamic interface to explore and test API endpoints directly.

## API Concepts and Principles

The WindFlag CTF platform API is designed with RESTful principles in mind, aiming for a stateless, client-server architecture that provides a clear and consistent way to interact with resources.

### RESTful Design

*   **Resources**: Almost every piece of data (e.g., a user, a challenge, a submission) is exposed as a resource identifiable by a unique URL.
*   **HTTP Methods**: Standard HTTP methods (GET, POST, PUT, DELETE) are used to perform actions on these resources:
    *   `GET`: Retrieve a resource or a collection of resources.
    *   `POST`: Create a new resource.
    *   `PUT`: Update an existing resource (full replacement).
    *   `PATCH`: Update an existing resource (partial modification).
    *   `DELETE`: Remove a resource.
*   **Statelessness**: Each request from a client to the server contains all the information needed to understand the request. The server does not store any client context between requests.
*   **JSON Format**: All request and response bodies are typically formatted as JSON (JavaScript Object Notation), which is lightweight and easily parsable by various programming languages.

### Error Handling

The API uses standard HTTP status codes to indicate the success or failure of a request. In case of an error, the API will return a JSON response body containing more detailed information about the error.

*   `200 OK`: The request was successful.
*   `201 Created`: A new resource was successfully created (e.g., after a `POST` request).
*   `204 No Content`: The request was successful, but there is no content to return (e.g., after a `DELETE` request).
*   `400 Bad Request`: The request was malformed or invalid. The response body will contain details on what was wrong (e.g., missing parameters, invalid data types).
*   `401 Unauthorized`: Authentication failed (e.g., missing or invalid `X-API-KEY` header).
*   `403 Forbidden`: The authenticated user does not have the necessary permissions to access the resource or perform the action.
*   `404 Not Found`: The requested resource could not be found.
*   `405 Method Not Allowed`: The HTTP method used is not supported for the requested resource.
*   `422 Unprocessable Entity`: The request was well-formed but could not be processed due to semantic errors (e.g., validation failed).
*   `500 Internal Server Error`: An unexpected error occurred on the server.

**Example Error Response:**

```json
{
    "message": "Validation failed",
    "errors": {
        "challenge_name": "Challenge name is required",
        "points": "Points must be a positive integer"
    }
}
```

### Rate Limiting

To ensure fair usage and protect against abuse, the WindFlag API may implement rate limiting. If you exceed the allowed number of requests within a given timeframe, the API will respond with a `429 Too Many Requests` status code. Details on rate limits (e.g., remaining requests, reset time) are often provided in HTTP response headers (e.g., `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`).

### API Versioning

The current API does not explicitly use versioning in the URL (e.g., `/api/v1/`). However, best practices suggest that for future extensibility, API changes that introduce breaking modifications should be handled with versioning. Developers should anticipate that future versions might introduce path-based or header-based versioning.

## Getting Started with the API

Follow these steps to quickly get started with interacting with the WindFlag API:

1.  **Generate Your API Key**: Log into your WindFlag instance, navigate to your user profile (or the Admin API Key section if you are an administrator), and generate a new API key. Copy this key.
2.  **Choose Your Tool**: You can use various tools to interact with the API:
    *   **`curl`**: For command-line testing.
    *   **Postman/Insomnia**: For graphical API development and testing.
    *   **Programming Languages**: Use HTTP client libraries in your preferred language (e.g., `requests` in Python, `fetch` in JavaScript).
3.  **Make Your First Request (Example: Get User Profile)**:

    Assuming your WindFlag instance is running locally at `http://127.0.0.1:5000`:

    ```bash
    curl -X GET \
      http://127.0.0.1:5000/api/v1/users/me \
      -H 'X-API-KEY: YOUR_GENERATED_API_KEY' \
      -H 'Content-Type: application/json'
    ```
    Replace `YOUR_GENERATED_API_KEY` with the actual key you generated.

    **Expected (successful) Response (Status 200 OK):**

    ```json
    {
        "id": 1,
        "username": "your_username",
        "email": "your_email@example.com",
        "is_admin": true,
        "is_super_admin": false,
        "score": 100,
        "hidden": false,
        "last_seen": "2025-11-24T12:34:56Z"
    }
    ```

    **Expected (error) Response (Status 401 Unauthorized):**

    ```json
    {
        "message": "Invalid API key"
    }
    ```

4.  **Explore Endpoints**: Refer to the detailed documentation for each specific API endpoint (linked above) to understand their available methods, parameters, and expected responses.
5.  **Develop Your Integration**: Start building your applications, scripts, or integrations using the API, always keeping security best practices in mind.