\### **Phase 1: The "Remove" (Preparation)**

*Before building, ensure your core is clean.*

- **[ ] Clean User Model:** Ensure `User` model has no residual "Team" or "Event" columns; it should be standalone.

- **[ ] Clean Routes:** Remove any hardcoded checks for specific events or teams in your current views.

- **[ ] Clean Dependencies:** Ensure `requirements.txt` only has what you are currently using (remove Celery/Authlib until needed).

---

### **Phase 2: The "Remake" (Implementation)**

*Implement these in order.*

#### **Step 1: Remake Team Logic (Tier 2)**

**Goal:** Allow users to group up.

- **[ ] Database:** Create `Team` model and add a `team_id` foreign key to the `User` model.

- **[ ] Logic:** Create a "Settings" toggle to enable/disable Team Mode.

- **[ ] Features:** Implement **Create**, **Join**, and **Leave** team functions.

- **[ ] Admin:** Add basic "Ban User" and "Delete Team" buttons in the Admin panel.

- **[ ] UI:** Update Scoreboard to show Team names instead of Usernames when the setting is on.

#### **Step 2: Remake Event Architecture (Tier 3)**

**Goal:** Allow the platform to run multiple CTFs.

- **[ ] Database:** Create an `Event` model.

- **[ ] Refactor:** Update `User`, `Team`, `Challenge`, and `Submission` to link to a specific `Event ID`.

- **[ ] Logic:** Update all database queries to filter by the *current* Event ID.

- **[ ] Auth:** Install Authlib and implement GitHub SSO (toggleable via settings).

- **[ ] Admin:** Differentiate roles: **Global Admin** (Makes events) vs **Event Admin** (Runs the event).

#### **Step 3: Polish & Real-time (Frontend)**

**Goal:** Make it look professional.

- **[ ] Visuals:** Add a WebSocket graph for live score updates (**Make this a toggleable Setting**).
