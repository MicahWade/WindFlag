### **Phase 1: The "Clean" (Preparation)**
* **[ ] Clean User Model:** Ensure the `User` model is standalone (remove any legacy "Team" or "Event" columns if they exist).
* **[ ] Clean Routes:** Remove any hardcoded checks for specific legacy events in your current views.
* **[ ] Clean Dependencies:** Audit `requirements.txt` and remove unused libraries (only keep what is currently running).

---

### **Phase 2: The "Upgrade" (Implementation)**

*Enhance the solo player experience and administration.*

#### **Step 1: Authentication & Admin**
* **[ ] Auth:** Install `Authlib` and implement **GitHub SSO** (allow users to log in with GitHub instead of email).
* **[ ] Admin:** Implement a simple **"Ban User"** button in the Admin panel to invalidate a user's tokens/session.

#### **Step 2: Polish & Real-time (Frontend)**
* **[ ] Visuals:** Add a **WebSocket graph** for live score updates on the scoreboard (users see their line go up in real-time).
* **[ ] Settings:** Create a toggle in `config.py` or the Admin panel to enable/disable the Live Graph (for performance).