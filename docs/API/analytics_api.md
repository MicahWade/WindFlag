# Analytics API Endpoints

This section details the API endpoints specifically designed for retrieving comprehensive analytics data within the WindFlag CTF Platform. These endpoints provide the raw data necessary to power dashboards and generate insights into user activity, challenge performance, and overall CTF progress.

## Authentication

All endpoints within the Analytics API namespace are privileged and require administrator authentication. Access is granted via a user-generated API key, which must correspond to an account with administrative permissions.

*   **Mechanism**: The API key must be securely transmitted in the `X-API-KEY` HTTP header for every request.
*   **Permissions**: Only API keys belonging to users with `is_admin: true` (or `is_super_admin: true`) privileges will be authorized to access these endpoints.
*   **Further Details**: For more comprehensive information on API key generation, management, and authentication protocols, please refer to the [API Overview](./api_overview.md) documentation.

## 1. GET /api/analytics

Retrieves various aggregated analytics and statistics for the entire platform or filtered by specific criteria.

*   **Description**: This endpoint provides a comprehensive JSON object containing a multitude of data points suitable for populating various charts and tables typically found in an admin analytics dashboard. It's designed to give administrators a holistic view of the CTF's performance and participant engagement.
*   **Method**: `GET`
*   **URL**: `/api/analytics`
*   **Authentication**: `X-API-KEY` header (required, admin user)
*   **Query Parameters**:
    *   `start_date` (string, ISO 8601 date-only, optional): Filters analytics data to include only events that occurred on or after this date. Format: `YYYY-MM-DD`.
    *   `end_date` (string, ISO 8601 date-only, optional): Filters analytics data to include only events that occurred on or before this date. Format: `YYYY-MM-DD`.
    *   `user_id` (integer, optional): Filters certain user-specific analytics (e.g., submissions) to focus on a single user.
    *   `challenge_id` (integer, optional): Filters challenge-specific analytics (e.g., solve rates) to focus on a single challenge.
    *   `category_id` (integer, optional): Filters category-specific analytics to focus on a single category.
    *   `limit_users` (integer, optional): Limits the number of top users returned in relevant data sets (e.g., `user_data`).
    *   `limit_challenges` (integer, optional): Limits the number of top challenges returned in relevant data sets (e.g., `challenge_solve_counts`).
*   **Example Request**:
    ```http
    GET /api/analytics?start_date=2023-10-01&end_date=2023-10-31&limit_users=5 HTTP/1.1
    Host: your-ctf-platform.com
    X-API-KEY: YOUR_ADMIN_API_KEY
    ```
*   **Example Response (Success - 200 OK)**:
    ```json
    {
        "category_data": {
            "labels": ["Category 1", "Category 2", "Awards", "Uncategorized"],
            "values": [1000, 800, 150, 200],
            "description": "Total points distributed per category, including awards."
        },
        "user_data": {
            "labels": ["admin1", "user1", "user2", "user3", "top_player"],
            "values": [1200, 750, 600, 550, 2000],
            "description": "Top users by score (or filtered if user_id is specified)."
        },
        "challenges_solved_over_time": {
            "dates": ["2023-10-01", "2023-10-02", "2023-10-03"],
            "counts": [5, 12, 8],
            "cumulative_solves": [5, 17, 25],
            "description": "Number of challenges solved per day and cumulative solves over time."
        },
        "cumulative_points_over_time": {
            "dates": ["2023-10-01T00:00:00Z", "2023-10-01T12:00:00Z", "2023-10-02T00:00:00Z"],
            "values": [0, 500, 1500],
            "description": "Platform-wide cumulative points over time."
        },
        "fails_vs_succeeds": {
            "labels": ["Succeeds", "Fails"],
            "values": [80, 20],
            "percentage": [80, 20],
            "description": "Ratio of correct versus incorrect flag submission attempts."
        },
        "challenge_solve_counts": {
            "labels": ["Challenge A", "Challenge B", "Challenge C"],
            "values": [15, 10, 7],
            "description": "Number of unique solves for each challenge."
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
            },
            "description": "Matrix showing which users have solved or attempted which challenges."
        },
        "total_users": 100,
        "total_challenges": 50,
        "active_challenges": 45,
        "total_submissions": 500,
        "last_updated": "2025-11-24T16:00:00Z",
        "generated_by": "admin_api_key_user"
    }
    ```
    *   **`category_data`**: Represents total points associated with each category.
        *   `labels` (array of strings): Names of categories.
        *   `values` (array of integers): Total points for each category.
        *   `description` (string): Explains the data set.
    *   **`user_data`**: Represents user scores.
        *   `labels` (array of strings): Usernames.
        *   `values` (array of integers): Scores for each user.
        *   `description` (string): Explains the data set.
    *   **`challenges_solved_over_time`**: Tracks the number of challenges solved daily and cumulatively.
        *   `dates` (array of strings, ISO 8601 date-only): Dates on which challenges were solved.
        *   `counts` (array of integers): Number of challenges solved on each corresponding date.
        *   `cumulative_solves` (array of integers): Cumulative count of challenges solved up to each date.
        *   `description` (string): Explains the data set.
    *   **`cumulative_points_over_time`**: Tracks the platform's total points accumulated over time.
        *   `dates` (array of strings, ISO 8601 datetime): Timestamps at which cumulative points were recorded.
        *   `values` (array of integers): Cumulative points at each corresponding timestamp.
        *   `description` (string): Explains the data set.
    *   **`fails_vs_succeeds`**: Statistics on flag submission attempts.
        *   `labels` (array of strings): Categories (e.g., "Succeeds", "Fails").
        *   `values` (array of integers): Raw counts for each category.
        *   `percentage` (array of integers): Percentage for each category.
        *   `description` (string): Explains the data set.
    *   **`challenge_solve_counts`**: Breakdown of how many times each challenge has been solved.
        *   `labels` (array of strings): Challenge names.
        *   `values` (array of integers): Number of solves for each challenge.
        *   `description` (string): Explains the data set.
    *   **`user_challenge_matrix`**: A detailed matrix showing user interactions with challenges.
        *   `users` (array of objects): List of user objects (id, username).
        *   `challenges` (array of objects): List of challenge objects (id, name).
        *   `status` (object): A nested object mapping `user_id` to another object mapping `challenge_id` to its status (`"solved"`, `"attempted"`, `"none"`).
        *   `description` (string): Explains the data set.
    *   **`total_users`** (integer): The total number of registered users.
    *   **`total_challenges`** (integer): The total number of challenges defined in the platform.
    *   **`active_challenges`** (integer): The number of challenges currently active (not hidden or past timed unlock).
    *   **`total_submissions`** (integer): The grand total of all flag submission attempts.
    *   **`last_updated`** (string, ISO 8601 datetime): The UTC timestamp when these analytics were last generated/cached.
    *   **`generated_by`** (string): The username associated with the API key that generated this report.
*   **Example Response (Error - 403 Forbidden)**:
    ```json
    {
        "message": "Administrator access required to retrieve analytics data.",
        "code": "ADMIN_ACCESS_REQUIRED"
    }
    ```
*   **Example Response (Error - 400 Bad Request)**:
    ```json
    {
        "message": "Invalid date format for 'start_date'. Expected YYYY-MM-DD.",
        "code": "BAD_REQUEST_VALIDATION"
    }
    ```
