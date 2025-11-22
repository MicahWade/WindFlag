# API Overview

This document provides an overview of the WindFlag CTF Platform API.

## Authentication

API access is secured using API Keys. To use the API, you must:
1. Generate an API Key through the user interface (your profile page).
2. Include your API Key in the `X-API-KEY` header for all authenticated requests.

## Endpoints

*   `/api/v1/status`: Check the API status and your authentication.
*   `/api/v1/users/me`: Retrieve information about the authenticated user.

For detailed information on available endpoints, request/response schemas, and authentication, please refer to the interactive API documentation available at `/api/docs`.
