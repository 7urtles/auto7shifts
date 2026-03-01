# Auto7Shifts

Automated shift-claiming tool for the 7shifts scheduling platform. Monitors the open shift pool and claims matching shifts based on configurable day, role, and location preferences.

---

<details>
<summary><h3>Overview</h3></summary>

Auto7Shifts authenticates against 7shifts' internal API, polls the open shift pool, and automatically claims shifts that match the user's configured preferences. It checks the user's existing schedule before claiming to prevent double-booking, and sends an SMS confirmation via Twilio when a shift is successfully claimed.

**Shift claim loop:**
1. Authenticate via 7shifts web session (cookie-based, `requests.Session`)
2. Read user account data: companies, locations, roles
3. Read current schedule to detect already-scheduled days
4. Poll shift pool via 7shifts' internal GraphQL API (`GetLegacyShiftPoolOffers`)
5. Filter available shifts against user preferences (day, role, location)
6. Claim matching shifts via `BidOnShiftPool` GraphQL mutation
7. Send SMS confirmation with shift details via Twilio

**SMS notification workflow:**
1. 7shifts sends an SMS to the configured Twilio number when a shift becomes available
2. Twilio forwards the payload to the Flask webhook endpoint
3. App parses the message body for shift pool notifications
4. On a match, triggers the claim flow and sends a confirmation SMS to the user

</details>

<details>
<summary><h3>Features</h3></summary>

- **Privilege detection**: reads the user's accessible companies, locations, and roles and presents them as selectable filter options in the CLI
- **Schedule conflict detection**: fetches the user's current week schedule before claiming; skips shifts on days already worked
- **Preference filtering**: user specifies target days, roles, and locations; only matching shifts are claimed
- **SMS notifications**: Twilio integration sends claim confirmations with shift time, date, role, position, and location
- **Session normalization**: sets `User-Agent` header to match the official 7shifts web app
- **Shift storage**: claimed and found shifts stored to SQLite via SQLAlchemy
- **Logging**: INFO-level log output to `auto7shifts/logs`

**Note:** 7shifts support confirmed that this tool does not violate their TOS, user, or API policies.

</details>

<details>
<summary><h3>Setup</h3></summary>

<details>
<summary><strong>Installation</strong></summary>

```bash
git clone https://github.com/7urtles/auto7shifts.git
cd auto7shifts
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

</details>

<details>
<summary><strong>Configuration</strong></summary>

Create a `.env` file in the project root:

```env
# 7shifts credentials
USER_EMAIL=your@email.com
USER_PASSWORD=yourpassword

# Twilio (optional — required for SMS notifications)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+18887776666
ACCOUNT_PHONE_NUMBER=+18887776666

# Secret slug protecting the Flask webhook URL
TWILIO_ENDPOINT=your_secret_endpoint_slug
```

</details>

<details>
<summary><strong>Running</strong></summary>

```bash
python3 cli.py
```

The CLI prompts for login, then presents menus to configure:
- Days to pick up shifts
- Roles to accept
- Locations to accept

</details>

</details>

<details>
<summary><h3>SMS Notifications</h3></summary>

Requires a Twilio account with an active phone number.

**Setup:**
1. Create a Twilio account and configure an SMS service at the Twilio console
2. In Sender Pool, click your registered number and set the webhook callback URL to your deployed Flask server:
   ```
   https://your-server.com/<TWILIO_ENDPOINT>
   ```
3. In 7shifts, set your contact number to the Twilio number and switch notifications from push to SMS

**How it works:**
- 7shifts sends a shift availability SMS to the Twilio number
- Twilio forwards the payload to the Flask webhook
- The app checks for "up for grabs" in the message body to identify shift pool notifications
- On a match, triggers the claim flow and sends a confirmation SMS to the user

**Required keys:**

| Key | Description |
|-----|-------------|
| `TWILIO_ACCOUNT_SID` | Found on Twilio home console |
| `TWILIO_AUTH_TOKEN` | Found on Twilio home console |
| `TWILIO_PHONE_NUMBER` | Your Twilio number (E.164 format) |
| `ACCOUNT_PHONE_NUMBER` | Your personal number for confirmations |
| `TWILIO_ENDPOINT` | Secret slug protecting the webhook URL |

</details>

<details>
<summary><h3>Architecture</h3></summary>

```
auto7shifts/
├── cli.py              # Terminal menu: login, preference selection
├── scraper.py          # SessionInstance: 7shifts API auth and data fetching
├── server.py           # Flask webhook server for Twilio SMS relay
├── requirements.txt
└── tools/
    ├── shift_tools.py  # Shift filtering, formatting, SQLite storage
    └── sms_tools.py    # Twilio SMS client wrapper
```

**`scraper.py` — SessionInstance:**
- `_login()`: POST to `/users/login`, stores session cookies
- `_read_user_info()`: GET `/api/v2/company/{id}/account` — companies, locations, roles
- `_read_user_schedule()`: GET `/api/v1/schedule/shifts` — current week schedule
- `_read_user_pool()`: POST `/gql` — `GetLegacyShiftPoolOffers` GraphQL query
- `pickup_shift()`: POST `/gql` — `BidOnShiftPool` GraphQL mutation
- `update_employee_data()`: GET `/api/v1/users` — full employee roster

</details>

<details>
<summary><h3>Stack</h3></summary>

Python, Flask, SQLAlchemy, SQLite, Requests, Twilio, python-dotenv, simple-term-menu

</details>

<details>
<summary><h3>License</h3></summary>

Private project - not for distribution.

</details>
