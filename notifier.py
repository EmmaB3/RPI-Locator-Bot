from typing import Sequence

from pi_locator_bot.models import PiSubscription, PiType, PiVendor, Subscriber, Team
from slack_sdk import WebClient


def send_restock_notification(tags: Sequence[str], text: str) -> None:
    type, vendor = None, None
    for tag in tags:
        tag = tag.lower()
        if type is None:
            type = PiType.query.filter_by(param_name=tag).first()
        if vendor is None:
            vendor = PiVendor.query.filter_by(param_name=tag).first()

    if None not in (type, vendor):
        subscribers = Subscriber.query.join(PiSubscription.query.filter(PiSubscription.vendors.any(id=vendor.id)).filter(PiSubscription.types.any(id=type.id)))

        for subscriber in subscribers:
            team = Team.query.get(subscriber.team)
            slack_client = WebClient(token=team.bot_token)

            slack_client.chat_postMessage(
                channel=subscriber.slack_id,
                text=text
            )
