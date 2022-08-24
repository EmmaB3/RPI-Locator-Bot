# NAME: views.py
# PURPOSE: chatbot API endpoint implementation
# AUTHOR: Emma Bethel
# CREATED: 8/22/22
# LAST EDITED: 8/23/22

import logging

from flask import make_response
from pi_locator_bot import slack_events_adapter
from pi_locator_bot.models import Team
from pi_locator_bot.messages import handle_message
from slack_sdk import WebClient

logging.basicConfig(level=logging.DEBUG)


@slack_events_adapter.on("message")
def respond_to_dm(payload):
    # for verifying endpoint w/ slack (delete later)
    challenge = payload.get('challenge')
    if challenge is not None:
        return make_response(challenge)

    team = Team.query.filter_by(id=payload['team_id']).first()
    user_id = payload['event']['user']

    # if message is a DM and didn't come from the bot itself, respond to it
    if user_id != team.bot_user_id and payload['event']['channel_type'] == 'im':
        message_text = payload['event']['text']
        slack_client = WebClient(token=team.bot_token)

        response_text = handle_message(message_text)

        slack_client.chat_postMessage(
            channel=user_id,
            text=response_text
        )

    return make_response()
