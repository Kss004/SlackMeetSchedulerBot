from calendar_utils import create_calendar_event

if __name__ == "__main__":
    slot = "Friday 1 PM"  # You can change this to anything
    event = create_calendar_event(slot, summary="Test Interview", description="This is a test event.")
    print("✅ Event created!")
    print(f"Link: {event.get('htmlLink')}")
