from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import os

load_dotenv()
client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

def send_slack_message(user_id, text):
    try:
        response = client.chat_postMessage(
            channel=user_id,
            text=text
        )
        return response
    except SlackApiError as e:
        print(f"Slack API Error: {e.response['error']}")
