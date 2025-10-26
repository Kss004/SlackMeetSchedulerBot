# Slack Interview Scheduler Bot with Google Calendar Integration

## Overview
This project automates the process of scheduling interviews between hiring managers and candidates via Slack, while automatically syncing selected slots to Google Calendar. The bot interacts with both parties, collects slot preferences, and books the confirmed slot in a shared calendar.

---

## Features
- **Slack Integration**: `/schedule @candidate slot1, slot2, slot3` command lets a manager send 3 interview slots to a candidate. The bot DMs the candidate with interactive buttons for slot selection (A, B, C). Candidate chooses a slot → Bot books the event into Google Calendar.
- **Google Calendar Integration**: Uses a service account to authenticate and insert events into a shared calendar. Supports automatic calculation of next weekday + slot time (e.g., next Wednesday 11 AM). Sends event link back to both parties on successful booking.
- **Robust Input Parsing**: Accepts a variety of slot formats and user mention formats.
- **Error Handling**: Handles Slack errors, DM permissions, and Google Calendar issues gracefully.

---

## Architecture
- **Bot Framework**: Slack Bolt for Python
- **Google API**: google-api-python-client
- **Secrets**: `.env` + `service_account.json`
- **Runtime**: Python 3.13 + venv
- **Deploy Mode**: Local (Socket Mode)

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repo-url>
cd slack-calendar-bot
```

### 2. Create and Activate a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the project root with the following:
```
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_SIGNING_SECRET=...
CALENDAR_ID=your-calendar@gmail.com
```
- `CALENDAR_ID` should be the email of the Google Calendar you want to use (not "primary").

### 5. Google Calendar Setup
- Create a Google Cloud project and enable the Google Calendar API.
- Create a service account and download the `service_account.json` file. Place it in the project root.
- Share your Google Calendar with the service account email (found in `service_account.json`) and give it "Make changes to events" permission.

### 6. Slack App Setup
- Create a Slack App at https://api.slack.com/apps
- Add the following OAuth scopes:
  - `chat:write`
  - `commands`
  - `app_mentions:read`
- Enable Socket Mode and copy the App Token.
- Install the app to your workspace and invite the bot to relevant channels or DM.
- Set up the `/schedule` slash command with usage hint: `/schedule @candidate Tuesday 3 PM, Wednesday 11 AM, Friday 1 PM`

---

## Usage
1. **Manager runs:**
   ```
   /schedule @candidate Tuesday 3 PM, Wednesday 11 AM, Friday 1 PM
   ```
2. **Bot DMs candidate:**
   - Presents slot options as interactive buttons (A, B, C).
3. **Candidate selects a slot:**
   - Bot books the event in Google Calendar and sends confirmation (with event link) to both candidate and manager.

---

## Troubleshooting
- **Bot not responding?**
  - Ensure the bot is invited to the channel or DM (`/invite @your-bot-name`).
- **Google Calendar event not visible?**
  - Make sure the service account has access to the calendar and `CALENDAR_ID` is set correctly.
- **Invalid blocks error?**
  - Ensure each button in the interactive message has a unique `action_id`.
- **User mention not working?**
  - Use Slack's mention format (`@user` or `<@USERID>`), or the raw user ID.

---

## Contribution Guidelines
- Fork the repo and create a feature branch.
- Submit a pull request with a clear description of your changes.
- For major changes, open an issue first to discuss what you’d like to change.

---

## License
MIT License 