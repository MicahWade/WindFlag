# Analytics API Endpoints

This section details the API endpoints for retrieving analytics data in the WindFlag CTF Platform.

## Authentication

All endpoints in the Analytics API namespace require administrator authentication using a user-generated API key. This key must be provided in the `X-API-KEY` header for every request.

For more information on generating and managing API keys, please refer to the [API Overview](./api_overview.md).

## 1. GET /api/analytics

Retrieves various analytics and statistics for the platform.

*   **Description**: Returns a comprehensive JSON object containing data for different charts and tables displayed in the admin analytics dashboard.
*   **Method**: `GET`
*   **URL**: `/api/analytics`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "category_data": {
            "labels": ["Category 1", "Category 2", "Awards"],
            "values": [1000, 800, 150]
        },
        "user_data": {
            "labels": ["admin1", "user1", "user2"],
            "values": [1200, 750, 600]
        },
        "challenges_solved_over_time": {
            "dates": ["2023-10-01", "2023-10-02"],
            "counts": [5, 12]
        },
        "cumulative_points_over_time": {
            "dates": ["2023-10-01T00:00:00Z", "2023-10-01T12:00:00Z"],
            "values": [0, 500]
        },
        "fails_vs_succeeds": {
            "labels": ["Succeeds", "Fails"],
            "values": [80, 20]
        },
        "challenge_solve_counts": {
            "labels": ["Challenge A", "Challenge B"],
            "values": [15, 10]
        },
        "user_challenge_matrix": {
            "users": [
                {"id": 1, "username": "admin1"},
                {"id": 2, "username": "user1"}
            ],
            "challenges": [
                {"id": 1, "name": "Challenge A"},
                {"id": 2, "name": "Challenge B"}
            ],
            "status": {
                "1": {"1": "solved", "2": "attempted"},
                "2": {"1": "solved", "2": "none"}
            }
        }
    }
    ```
