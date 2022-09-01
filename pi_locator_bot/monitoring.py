# NAME: monitoring.py
# PURPOSE: helpers for error reporting and metric collection
# AUTHOR: Emma Bethel
# CREATED: 8/31/22
# LAST EDITED: 8/31/22

from pi_locator_bot.models import Subscriber, Team
from slack_sdk import WebClient

def report_error(error):
    admins = Subscriber.query.filter_by(is_admin=True)

    for admin in admins:
        team = Team.query.get(admin.team)
        slack_client = WebClient(token=team.bot_token)

        slack_client.chat_postMessage(
            channel=admin.slack_id,
            text=f'Error: {error}'
        )
