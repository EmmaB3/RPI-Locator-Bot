# NAME: listener.py
# PURPOSE: tracking raspberry pi restocks and notifying subscribed users accordingly
# AUTHOR: Emma Bethel
# CREATED: 8/18/22
# LAST EDITED: 9/14/22

import argparse
import time
import feedparser

from pi_locator_bot.monitoring import report_error
from notifier import send_restock_notification


def listen_for_restocks():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--start-time',
        type=str,
        help='Time after which events should be considered "new" on the first poll of the RSS feed. Should be in GMT '
             'w/ format MM-DD-YYYY HH:MM:SS'
    )

    args = parser.parse_args()


    if args.start_time is None:
        last_refresh_time = time.gmtime(time.time())
    else:
        last_refresh_time = time.strptime(args.start_time, '%m-%d-%Y %H:%M:%S')

    while True:
        try:
            print(f'listening for new restocks since {last_refresh_time}...')
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