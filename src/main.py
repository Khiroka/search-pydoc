import os
import re
from pprint import pprint

from flask import Flask
import requests
from slack import WebClient
from slackeventsapi import SlackEventAdapter

import pysearch

app = Flask(__name__)
slack_signing_secret = os.environ["SIGINING"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events", app)

slack_bot_token = os.environ["PYDOC_TOKEN"]
slack_client = WebClient(slack_bot_token)


def block_format(matches):
    text = ""
    for name, url in matches.items():
        text += f"<{url}|{name}>\n"

    fmt = [
        {"type": "divider"},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": text},
        },
    ]
    return fmt


@slack_events_adapter.on("message")
def main(event_data):
    message = event_data["event"]
    channel = message["channel"]

    if message.get("subtype") is None and re.match(r"^py\s", message.get("text")):
        word = message.get("text").split()[1]
        matches = pysearch.main(word)

        slack_client.chat_postMessage(
            channel=channel,
            blocks=block_format(matches),
        )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
