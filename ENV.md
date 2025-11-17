# Environment Variables

This file documents the environment variables used by the WindFlag application.

## `.env` File

The application uses a `.env` file to manage environment variables. You can create a `.env` file in the root of the project and add the following variables:

-   `SECRET_KEY`: A secret key for the application. This is used to keep the client-side sessions secure.
-   `DATABASE_URL`: The URL for the database. For example, `sqlite:///app.db`.
-   `REQUIRE_JOIN_CODE`: Set to `True` to require a join code for new user registrations. Set to `False` (default) to allow anyone to register without a join code.
-   `JOIN_CODE`: The specific code that users must enter to register if `REQUIRE_JOIN_CODE` is set to `True`. This variable is ignored if `REQUIRE_JOIN_CODE` is `False`.
-   `REQUIRE_EMAIL`: Set to `False` to make the email field optional during user registration. Set to `True` (default) to make it a required field.

## `.env.template`

A `.env.template` file is provided as a template for the `.env` file. You can copy this file to `.env` and fill in the values.
