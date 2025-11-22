# API Overview

This document provides an overview of the WindFlag CTF Platform API.

## Authentication

API access is secured using API Keys. To use the API, you must:
1. Generate an API Key through the user interface (your profile page).
2. Include your API Key in the `X-API-KEY` header for all authenticated requests.

## Endpoints

For detailed information on the API endpoints, refer to the following sections:

*   **[Core API Endpoints](core_api.md)**: Includes general API status and user profile information.
*   **[Challenges API Endpoints](challenges_api.md)**: Provides endpoints for managing challenges.
*   **[Category API Endpoints](categories_api.md)**: Provides endpoints for managing challenge categories.
*   **[User API Endpoints](users_api.md)**: Provides endpoints for managing user information (admin only).
*   **[Award Category API Endpoints](award_categories_api.md)**: Provides endpoints for managing award categories.
*   **[Award API Endpoints](awards_api.md)**: Provides an endpoint for giving awards to users.
*   **[Settings API Endpoints](settings_api.md)**: Provides endpoints for managing application settings.
*   **[Submission API Endpoints](submissions_api.md)**: Provides an endpoint for retrieving all challenge submissions.
*   **[Analytics API Endpoints](analytics_api.md)**: Provides an endpoint for retrieving various analytics and statistics.

For interactive API documentation with request/response schemas, please refer to the live documentation available at `/api/docs`.
