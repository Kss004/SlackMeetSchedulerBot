import os
from datetime import datetime, timedelta
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
import re

load_dotenv()


def create_calendar_event(slot_str, summary="Interview", description="Interview slot booked"):
    # Load credentials
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    SERVICE_ACCOUNT_FILE = 'service_account.json'

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=credentials)

    # Parse slot: e.g. "Wednesday 11 AM"
    # Normalize and split
    slot_str = slot_str.strip()
    match = re.match(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d{1,2})\s*(AM|PM)$", slot_str, re.IGNORECASE)
    if not match:
        raise ValueError("Slot format should be like 'Wednesday 11 AM'")

    day_name = match.group(1).capitalize()
    hour = int(match.group(2))
    ampm = match.group(3).upper()
    time_part = f"{hour} {ampm}"


    # Compute next matching weekday
    timezone = pytz.timezone("Asia/Kolkata")
    today = datetime.now(timezone)
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    target_day_index = weekdays.index(day_name)
    days_ahead = (target_day_index - today.weekday() + 7) % 7
    if days_ahead == 0:
        days_ahead = 7  # Next week

    target_date = today + timedelta(days=days_ahead)
    target_time = datetime.strptime(time_part, "%I %p").time()
    event_start = timezone.localize(datetime.combine(target_date.date(), target_time))
    event_end = event_start + timedelta(minutes=30)

    # Create event object
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': event_start.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': event_end.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
    }

    # Get calendar ID from .env or default to 'primary'
    calendar_id = os.getenv("CALENDAR_ID", "primary")
    # Insert event and send email
    created_event = service.events().insert(
        calendarId=calendar_id,
        body=event,
        sendUpdates="all"  # ensures attendee gets notified
    ).execute()

    return created_event
