import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from calendar_utils import create_calendar_event
from dotenv import load_dotenv

load_dotenv()

# Slack credentials
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

app = App(token=SLACK_BOT_TOKEN)

@app.command("/schedule")
def handle_schedule_command(ack, respond, command):
    ack()
    text = command.get("text", "").strip()

    if not text:
        respond("Please provide a slot like `Wednesday 11 AM`.\nExample: `/schedule Wednesday 11 AM`")
        return

    try:
        event = create_calendar_event(text, summary="Interview with Candidate", description="Scheduled via Slack bot")
        event_link = event.get("htmlLink")
        respond(f"✅ Interview scheduled for *{text}*.\n📅 [View on Calendar]({event_link})")
    except Exception as e:
        respond(f"❌ Failed to schedule interview.\nError: {str(e)}")

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
