# Challenges API Endpoints

This section details the API endpoints related to challenges, specifically for retrieving dynamic flags.

## 1. GET /challenges/<int:challenge_id>/dynamic_flag

Retrieves a dynamic flag for a specific challenge, provided the challenge supports dynamic flags and the correct challenge-specific API key is supplied.

*   **Description**: This endpoint allows authorized clients to obtain a dynamically generated flag for a challenge. This is particularly useful for challenges where the flag changes frequently or is unique per request/instance.
*   **Method**: `GET`
*   **URL**: `/api/v1/challenges/<int:challenge_id>/dynamic_flag`
*   **Authentication**: `X-Dynamic-Flag-API-KEY` header (required). This is a *challenge-specific* API key, distinct from the user's general API key. It is configured by administrators for challenges that utilize dynamic flags.
*   **Path Parameters**:
    *   `challenge_id` (integer, required): The unique identifier of the challenge for which to retrieve the dynamic flag.
*   **Example Request**:
    ```http
    GET /api/v1/challenges/123/dynamic_flag HTTP/1.1
    Host: your-ctf-platform.com
    X-Dynamic-Flag-API-KEY: YOUR_CHALLENGE_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "challenge_id": 123,
        "dynamic_flag": "FLAG{123-anonymous-some_random_string}"
    }
    ```
*   **Example Response (Error - 404 Not Found)**:
    ```json
    {
        "message": "Challenge with ID 123 not found."
    }
    ```
*   **Example Response (Error - 403 Forbidden - Dynamic Flags Not Supported)**:
    ```json
    {
        "message": "Challenge 123 does not support dynamic flags."
    }
    ```
*   **Example Response (Error - 401 Unauthorized - Missing Key)**:
    ```json
    {
        "message": "Dynamic Flag API Key is missing."
    }
    ```
*   **Example Response (Error - 401 Unauthorized - Invalid Key)**:
    ```json
    {
        "message": "Invalid Dynamic Flag API Key."
    }
    ```
