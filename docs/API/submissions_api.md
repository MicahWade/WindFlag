# Submission API Endpoints

This section details the API endpoints for retrieving challenge submissions in the WindFlag CTF Platform.

## Authentication

All endpoints in the Submission API namespace require administrator authentication using a user-generated API key. This key must be provided in the `X-API-KEY` header for every request.

For more information on generating and managing API keys, please refer to the [API Overview](./api_overview.md).

## 1. GET /api/submissions

Retrieves a list of all challenge submissions.

*   **Description**: Returns an array of all challenge submissions, including user, challenge, timestamp, and score at submission. This endpoint is for administrative purposes.
*   **Method**: `GET`
*   **URL**: `/api/submissions`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Example Response (Success - 200 OK)**:
    ```json
    [
        {
            "id": 1,
            "user_id": 1,
            "challenge_id": 1,
            "timestamp": "2023-10-27T10:00:00.000Z",
            "score_at_submission": 100
        },
        {
            "id": 2,
            "user_id": 2,
            "challenge_id": 1,
            "timestamp": "2023-10-27T10:05:00.000Z",
            "score_at_submission": 120
        }
    ]
    ```
