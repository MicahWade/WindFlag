# Admin Panel Challenge Visibility

The Admin Panel's "Manage Challenges" section provides enhanced visual cues to help administrators quickly understand the visibility and accessibility status of each challenge. Challenges may appear with different background "stripes" (colors) to indicate their state.

## Visibility States and Their Meanings

Each challenge in the table can have one of the following visual indicators:

*   **<span style="background-color: rgba(220, 38, 38, 0.5); padding: 2px 5px; border-radius: 3px;">Red Stripe (Hidden for All Users)</span>**
    *   **Meaning**: This challenge has been explicitly marked as `is_hidden = True`. It will not be visible to any non-admin users, regardless of their progress or any unlock conditions. This is typically used for challenges under development, retired challenges, or challenges meant only for internal testing.
    *   **Admin Action**: Administrators can toggle this setting when creating or updating a challenge.

*   **<span style="background-color: rgba(202, 138, 4, 0.5); padding: 2px 5px; border-radius: 3px;">Yellow Stripe (Locked by Prerequisites)</span>**
    *   **Meaning**: This challenge is currently locked for the *current administrator* due to unmet prerequisites (e.g., a certain percentage of challenges not completed, a specific number of challenges not solved, or a timed unlock date not yet reached). While it might be visible to regular users, they cannot access it until they meet the specified conditions.
    *   **Admin Action**: This status helps administrators understand why a challenge might not be accessible to users. It reflects the challenge's `unlock_type` and associated `prerequisite_` fields.

*   **<span style="background-color: rgba(37, 99, 235, 0.5); padding: 2px 5px; border-radius: 3px;">Blue Stripe (Rarely Unlocked)</span>**
    *   **Meaning**: This challenge is currently unlocked by less than 50% of eligible users (non-admin, non-hidden users). This indicates that the challenge might be particularly difficult, obscure, or its prerequisites are only met by a small subset of the user base.
    *   **Admin Action**: This status can help administrators identify challenges that might need re-evaluation (e.g., adjusting difficulty, hints, or prerequisites) if the goal is broader accessibility.

*   **No Stripe (Visible)**
    *   **Meaning**: This challenge is not explicitly hidden, is not locked by prerequisites for the current administrator, and is unlocked by 50% or more of eligible users. It is generally accessible and visible to users who meet its basic unlock criteria.

## How to Interpret

The visual stripes provide a quick overview:
*   **Red** indicates a challenge that is intentionally kept from general view.
*   **Yellow** highlights challenges that are part of the progression system but are not yet accessible due to conditions.
*   **Blue** points to challenges that are accessible but have a low engagement rate among the user base.

By using these visual cues, administrators can more effectively manage challenge visibility, balance difficulty, and ensure a smooth user experience.

## Dynamic Flags

The platform supports dynamic flags, which are flags that change for each user. This is useful for preventing flag sharing and ensuring that each user has to solve the challenge themselves.

### Configuration

To configure a dynamic flag for a challenge, follow these steps:

1.  **Set Flag Type to "Dynamic"**: When creating or editing a challenge, set the "Flag Type" to "Dynamic". This will reveal the "Dynamic Flag Settings" section on the challenge edit page.

2.  **Generate API Key**: Once the challenge is created, you will see the "Dynamic Flag Settings" section. Click on "Generate New Dynamic Flag API Key" to generate a new API key for the challenge. **Save this key, as it will not be shown again.**

### Your Application

Your application should expose an endpoint that accepts a `POST` request with a JSON body containing `user_id`. Your endpoint should return a JSON response with a `flag` key, which contains the dynamic flag for the user. You must include the generated API key in the `X-API-KEY` header of the request to your endpoint.

#### Example Request

```
POST /your-dynamic-flag-endpoint
Host: your-server.com
Content-Type: application/json
X-API-KEY: your_generated_api_key

{
    "user_id": 123
}
```

#### Example Response

```json
{
    "flag": "flag{this_is_a_dynamic_flag_for_user_123}"
}
```
