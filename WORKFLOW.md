# Slack Interview Scheduler Bot - Workflow Documentation

## System Overview

This Slack bot automates the interview scheduling process between hiring managers and candidates by integrating Slack communications with Google Calendar. The system provides a seamless experience for both parties while automatically managing calendar events.

## Architecture Components

### 1. **Core Components**
- **Slack Bot (`app.py`)**: Main application handling Slack interactions
- **Google Calendar Utils (`calendar_utils.py`)**: Google Calendar API integration
- **Slack Utils (`slack_utils.py`)**: Slack SDK utilities
- **State Management (`state.py`)**: Temporary storage for slot selections
- **Configuration**: Environment variables and service account credentials

### 2. **External Integrations**
- **Slack API**: Bot interactions, slash commands, interactive messages
- **Google Calendar API**: Event creation and management
- **Google Service Account**: Authentication for calendar access

---

## Detailed Workflow

### Phase 1: Manager Initiates Scheduling

```
📱 Manager in Slack Channel/DM
    ↓
💬 Types: /schedule @candidate Tuesday 3 PM, Wednesday 11 AM, Friday 1 PM
    ↓
🤖 Bot receives slash command
    ↓
🔍 Bot parses command:
    - Extracts candidate user ID
    - Parses 3 time slots using regex
    - Validates format and slot count
    ↓
📊 Bot stores temporary state:
    slot_options_map[candidate_id] = {
        "slots": [parsed_slots],
        "manager_id": manager_id
    }
```

### Phase 2: Candidate Interaction

```
🤖 Bot creates interactive message with buttons:
    - Button A: First slot option
    - Button B: Second slot option  
    - Button C: Third slot option
    ↓
📤 Bot sends DM to candidate with interactive buttons
    ↓
👤 Candidate receives DM with slot selection buttons
    ↓
🖱️ Candidate clicks preferred slot button (A, B, or C)
    ↓
🤖 Bot receives button interaction event
```

### Phase 3: Calendar Event Creation

```
🤖 Bot processes slot selection:
    - Retrieves stored slot data
    - Gets selected slot based on button value
    ↓
📅 Bot calls Google Calendar API:
    - Authenticates using service account
    - Parses slot string (e.g., "Wednesday 11 AM")
    - Calculates next occurrence of specified weekday
    - Creates 30-minute calendar event
    - Sets timezone to Asia/Kolkata
    ↓
✅ Google Calendar creates event and returns event details
```

### Phase 4: Confirmation and Cleanup

```
📨 Bot sends confirmation messages:
    - To candidate: "✅ Interview scheduled for [slot]"
    - To manager: "✅ Interview confirmed for [slot]"
    - Both receive calendar event link
    ↓
🧹 Bot cleans up temporary state:
    - Removes candidate data from slot_options_map
    ↓
✅ Process complete
```

---

## Flowchart Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           SLACK INTERVIEW SCHEDULER BOT                          │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   📱 Manager     │    │   🤖 Slack Bot   │    │ 📅 Google Cal   │    │   👤 Candidate   │
│                 │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │ /schedule @candidate  │                       │                       │
         │ Tue 3PM, Wed 11AM,    │                       │                       │
         │ Fri 1PM               │                       │                       │
         ├──────────────────────▶│                       │                       │
         │                       │                       │                       │
         │                       │ 1. Parse command      │                       │
         │                       │ 2. Extract slots      │                       │
         │                       │ 3. Validate format    │                       │
         │                       │ 4. Store temp state   │                       │
         │                       │                       │                       │
         │                       │ Send interactive msg  │                       │
         │                       │ with A/B/C buttons    │                       │
         │                       ├──────────────────────────────────────────────▶│
         │                       │                       │                       │
         │                       │                       │                       │ User clicks
         │                       │                       │                       │ Button A/B/C
         │                       │◀──────────────────────────────────────────────┤
         │                       │                       │                       │
         │                       │ 1. Get selected slot  │                       │
         │                       │ 2. Parse date/time    │                       │
         │                       │ 3. Create event       │                       │
         │                       ├──────────────────────▶│                       │
         │                       │                       │                       │
         │                       │                       │ 1. Auth via service   │
         │                       │                       │    account           │
         │                       │                       │ 2. Calculate next     │
         │                       │                       │    weekday           │
         │                       │                       │ 3. Create 30min      │
         │                       │                       │    event             │
         │                       │                       │ 4. Return event link │
         │                       │◀──────────────────────┤                       │
         │                       │                       │                       │
         │ ✅ Confirmation +     │                       │                       │
         │ 📅 Event link        │                       │                       │
         │◀──────────────────────┤                       │                       │
         │                       │                       │                       │
         │                       │ ✅ Confirmation +     │                       │
         │                       │ 📅 Event link        │                       │
         │                       ├──────────────────────────────────────────────▶│
         │                       │                       │                       │
         │                       │ 🧹 Cleanup temp      │                       │
         │                       │    state              │                       │
         │                       │                       │                       │
```

---

## Error Handling Scenarios

### 1. **Invalid Command Format**
- **Trigger**: Manager doesn't provide proper format
- **Response**: Bot sends usage instructions
- **Example**: `/schedule` without candidate mention

### 2. **Insufficient Slots**
- **Trigger**: Less than 3 valid slots provided
- **Response**: Bot requests exactly 3 slots
- **Example**: `/schedule @user Tuesday 3PM` (only 1 slot)

### 3. **DM Permission Issues**
- **Trigger**: Bot cannot send DM to candidate
- **Response**: Bot notifies manager about permission issue
- **Solution**: Candidate must DM bot first or invite bot to channel

### 4. **Calendar API Errors**
- **Trigger**: Google Calendar API call fails
- **Response**: Bot logs error and notifies users
- **Common causes**: Service account permissions, quota limits

### 5. **Invalid Slot Format**
- **Trigger**: Slot doesn't match expected pattern
- **Response**: Bot rejects slot and provides format examples
- **Example**: "Tomorrow 3PM" (doesn't specify weekday)

---

## Data Flow

### 1. **Input Processing**
```
Raw Input: "/schedule @U1234567 Tuesday 3 PM, Wednesday 11 AM, Friday 1 PM"
    ↓
Parsed Components:
- candidate_id: "U1234567"
- slots: ["Tuesday 3 PM", "Wednesday 11 AM", "Friday 1 PM"]
- manager_id: "U7654321"
```

### 2. **State Management**
```
Temporary Storage:
slot_options_map = {
    "U1234567": {
        "slots": ["Tuesday 3 PM", "Wednesday 11 AM", "Friday 1 PM"],
        "manager_id": "U7654321"
    }
}
```

### 3. **Calendar Event Creation**
```
Input: "Tuesday 3 PM"
    ↓
Calculations:
- Current date: July 11, 2025 (Friday)
- Target day: Tuesday (next week)
- Target date: July 15, 2025
- Event time: 3:00 PM - 3:30 PM IST
    ↓
Google Calendar Event:
- Summary: "Interview"
- Start: 2025-07-15T15:00:00+05:30
- End: 2025-07-15T15:30:00+05:30
- Calendar: shashwat.sandilya@gmail.com
```

---

## Configuration Requirements

### 1. **Environment Variables (.env)**
```
SLACK_BOT_TOKEN=xoxb-...          # Bot OAuth token
SLACK_APP_TOKEN=xapp-...          # Socket mode app token
SLACK_SIGNING_SECRET=...          # App signing secret
CALENDAR_ID=email@gmail.com       # Target calendar email
```

### 2. **Slack App Permissions**
- `chat:write` - Send messages
- `commands` - Handle slash commands
- `app_mentions:read` - Read mentions

### 3. **Google Calendar Setup**
- Service account with Calendar API access
- Calendar shared with service account email
- "Make changes to events" permission granted

---

## Security Considerations

### 1. **Credential Management**
- Service account key stored securely
- Environment variables for sensitive data
- No hardcoded secrets in source code

### 2. **Input Validation**
- Regex validation for slot formats
- User ID validation for mentions
- Sanitization of user inputs

### 3. **Access Control**
- Bot requires proper Slack permissions
- Calendar access limited to service account
- Temporary state cleanup prevents data leakage

---

## Performance Considerations

### 1. **State Management**
- In-memory storage for temporary data
- Automatic cleanup after slot selection
- Scales with concurrent users

### 2. **API Rate Limits**
- Google Calendar API quotas
- Slack API rate limiting
- Error handling for quota exhaustion

### 3. **Response Times**
- Slack acknowledgments within 3 seconds
- Asynchronous calendar operations
- Background processing for notifications

---

## Future Enhancements

### 1. **Advanced Features**
- Multiple timezone support
- Recurring interview slots
- Integration with video conferencing
- Automated reminder notifications

### 2. **Persistence**
- Database storage for slot history
- User preference management
- Analytics and reporting

### 3. **UI Improvements**
- Rich interactive messages
- Calendar preview in Slack
- Drag-and-drop scheduling interface

---

## Troubleshooting Guide

### Common Issues and Solutions

1. **Bot not responding to commands**
   - Check if bot is installed in workspace
   - Verify OAuth scopes are configured
   - Ensure Socket Mode is enabled

2. **Calendar events not created**
   - Verify service account permissions
   - Check calendar sharing settings
   - Validate CALENDAR_ID in environment

3. **Interactive buttons not working**
   - Confirm unique action_id for each button
   - Check Slack app interactivity settings
   - Verify button payload structure

4. **Time zone issues**
   - Calendar events default to Asia/Kolkata
   - Modify timezone in calendar_utils.py
   - Consider user-specific timezone handling

This workflow documentation provides a complete understanding of how the Slack Interview Scheduler Bot operates, from initial command to final calendar event creation.
