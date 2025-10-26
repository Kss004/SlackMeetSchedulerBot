import os
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from calendar_utils import create_calendar_event
from slack_sdk.errors import SlackApiError

load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

# Store temporary slot state
slot_options_map = {}  # format: {candidate_id: {"slots": [..], "manager_id": ...}}

# Regex pattern to flexibly match date/time slots (e.g., Tue 3pm, Wednesday 11:00, Fri 1 PM, etc.)
SLOT_PATTERN = re.compile(r"([A-Za-z]{3,9}\s*\d{1,2}\s*(?:AM|PM|am|pm)?)")


def extract_slots(text):
    # Try to extract up to 3 slot expressions from the text
    # Accepts formats like: Tue 3pm, Wednesday 11:00, Fri 1 PM, 3pm Tuesday, etc.
    # Returns a list of up to 3 slots, or an empty list if not found
    # Normalize to 'Day Time AM/PM' format
    # Accepts both comma and space separated
    # Example matches: 'Tuesday 3 PM', 'Wed 11am', 'Fri 1 PM'
    # This can be improved further for more natural language
    matches = re.findall(r"([A-Za-z]{3,9}\s*\d{1,2}\s*(?:AM|PM|am|pm)?)", text)
    slots = [m.strip().title().replace("Am", "AM").replace("Pm", "PM") for m in matches]
    return slots[:3]


@app.command("/schedule")
def handle_schedule_command(ack, body, say, client):
    ack()
    text = body.get("text", "").strip()

    # Extract candidate mention in any of these formats: <@USERID>, @USERID, USERID
    mention_match = re.match(r"(?:<@([A-Z0-9]+)>|@([A-Z0-9]+)|([A-Z0-9]+)) ?(.*)", text)
    if not mention_match:
        say("❌ Please use the format: `/schedule @candidate Tuesday 3 PM, Wednesday 11 AM, Friday 1 PM`")
        return

    candidate_id = mention_match.group(1) or mention_match.group(2) or mention_match.group(3)
    slots_text = mention_match.group(4)
    slots = extract_slots(slots_text)

    print(f"[DEBUG] Slots extracted: {slots}")  # Debug print

    if len(slots) != 3 or any(not s for s in slots):
        say("❌ Please provide exactly 3 valid interview slots (e.g., Tuesday 3 PM, Wednesday 11 AM, Friday 1 PM). You can use any common format.")
        return

    # Truncate slot text for button labels to 70 chars (Slack limit is 75)
    slots = [s[:70] for s in slots]

    manager_id = body["user_id"]
    slot_options_map[candidate_id] = {
        "slots": slots,
        "manager_id": manager_id,
    }

    # Send interactive options to candidate (now with two buttons for testing)
    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*Choose your preferred interview slot:*"}
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": f"A) {slots[0]}", "emoji": True},
                    "value": "0",
                    "action_id": "slot_chosen_A"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": f"B) {slots[1]}", "emoji": True},
                    "value": "1",
                    "action_id": "slot_chosen_B"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": f"C) {slots[2]}", "emoji": True},
                    "value": "2",
                    "action_id": "slot_chosen_C"
                }
            ]
        }
    ]
    print(f"[DEBUG] Blocks payload: {blocks}")  # Debug print
    try:
        client.chat_postMessage(
            channel=candidate_id,
            text="Please select your preferred interview slot.",
            blocks=blocks
        )
        say(f"✅ Sent slot selection to <@{candidate_id}>.")
    except SlackApiError as e:
        if e.response["error"] == "not_in_channel":
            say(f"❌ The bot is not in a DM with <@{candidate_id}>. Please ask them to DM the bot first, or invite the bot to the channel.")
        elif e.response["error"] == "invalid_blocks":
            say(f"❌ Failed to send interactive message to candidate due to a Slack formatting error. Here are the slots:\nA) {slots[0]}\nB) {slots[1]}\nC) {slots[2]}")
        else:
            say(f"❌ Failed to send message to candidate: {e.response['error']}")
    return

# Update the action handler to accept all three action_ids
@app.action(re.compile(r"slot_chosen_[ABC]"))
def handle_slot_selection(ack, body, client, respond):
    ack()
    candidate_id = body["user"]["id"]
    selected_index = int(body["actions"][0]["value"])

    entry = slot_options_map.get(candidate_id)
    if not entry:
        respond("❌ Couldn't find any active slot selection. Please try again.")
        return

    slots = entry["slots"]
    manager_id = entry["manager_id"]
    selected_slot = slots[selected_index]

    # Book calendar event
    event = create_calendar_event(selected_slot)
    event_link = event.get("htmlLink")

    confirmation_msg = f"✅ Interview confirmed for *{selected_slot}*.\n📅 <{event_link}|View Event>"

    # Notify both candidate and manager
    for user in [candidate_id, manager_id]:
        try:
            client.chat_postMessage(channel=user, text=confirmation_msg)
        except Exception:
            pass

    respond(f"✅ Thanks! Interview scheduled for *{selected_slot}*.")

    # Cleanup
    slot_options_map.pop(candidate_id, None)


if __name__ == "__main__":
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()
