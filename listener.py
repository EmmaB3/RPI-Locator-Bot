# NAME: listener.py
# PURPOSE: tracking raspberry pi restocks and notifying subscribed users accordingly
# AUTHOR: Emma Bethel
# CREATED: 8/18/22
# LAST EDITED: 8/18/22

import time
import feedparser

from pi_locator_bot.monitoring import report_error
from notifier import send_restock_notification


def listen_for_restocks():
    last_refresh_time = time.gmtime(time.time())

    while True:
        try:
            print('listening...')
            loop_start_time = time.gmtime(time.time())
            feed_contents = feedparser.parse('https://rpilocator.com/feed')

            restocks = feed_contents['entries']
            for restock in restocks:
                if restock['published_parsed'] <= last_refresh_time:
                    break

                send_restock_notification([tag['term'] for tag in restock['tags']], restock['title'])

            last_refresh_time = loop_start_time
        except Exception as e:
            report_error(e)
        time.sleep(60)


if __name__ == '__main__':
    listen_for_restocks()