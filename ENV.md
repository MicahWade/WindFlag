# Environment Variables

This file documents the environment variables used by the WindFlag application.

## `.env` File

The application uses a `.env` file to manage environment variables. You can create a `.env` file in the root of the project and add the following variables:

-   `SECRET_KEY`: A secret key for the application. This is used to keep the client-side sessions secure.
-   `DATABASE_URL`: The URL for the database. For example, `sqlite:///app.db`.
-   `JOIN_CODE`: An optional join code that can be required for new users to register.

## `.env.template`

A `.env.template` file is provided as a template for the `.env` file. You can copy this file to `.env` and fill in the values.
