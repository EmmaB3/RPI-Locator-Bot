# NAME: notifier.py
# PURPOSE: utils for sending restock notifications
# AUTHOR: Emma Bethel
# CREATED: 9/17/22

from typing import Sequence

from pi_locator_bot.models import PiSubscription, PiType, PiVendor, Subscriber, Workspace
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def send_restock_notification(tags: Sequence[str], text: str) -> Sequence[Sequence[str]]:
    type, vendor = None, None
    for tag in tags:
        tag = tag.lower()
        if type is None:
            type = PiType.query.filter_by(param_name=tag).first()
        if vendor is None:
            vendor = PiVendor.query.filter_by(param_name=tag).first()

    failures = []
    if None not in (type, vendor):
        subscribers = Subscriber.query.join(PiSubscription.query.filter(PiSubscription.vendors.any(id=vendor.id)).filter(PiSubscription.types.any(id=type.id)))

        for subscriber in subscribers:
            workspace = Workspace.query.get(subscriber.workspace)
            slack_client = WebClient(token=workspace.bot_token)

            try:
                slack_client.chat_postMessage(
                    channel=subscriber.slack_id,
                    text=text
                )
            except SlackApiError as e:
                failures.append((workspace.name, subscriber.slack_id, str(e)))
        
    return failures
