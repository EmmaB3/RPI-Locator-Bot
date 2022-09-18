# NAME: commands.py
# PURPOSE: custom flask cli commands
# AUTHOR: Emma Bethel
# CREATED: 9/17/22

import time
import click
import feedparser

from pi_locator_bot import app
from pi_locator_bot.monitoring import report_error
from pi_locator_bot.notifier import send_restock_notification


@app.cli.command("listen-for-restocks")
@click.option("--start-time", required=False, type=str,
                help='Time after which events should be considered "new" on the first poll of the RSS feed. Should be '
                'in GMT with format \'MM-DD-YYYY HH:MM:SS\'.')
def listen_for_restocks(start_time):
    if start_time is None:
        last_refresh_time = time.gmtime(time.time())
    else:
        last_refresh_time = time.strptime(start_time, '%m-%d-%Y %H:%M:%S')
    
    failure_count = 0

    while True:
        try:
            print(f'listening for new restocks since {last_refresh_time}...')
            loop_start_time = time.gmtime(time.time())
            feed_contents = feedparser.parse('https://rpilocator.com/feed')

            restocks = feed_contents['entries']
            for restock in restocks:
                if restock['published_parsed'] <= last_refresh_time:
                    break

                failures = send_restock_notification([tag['term'] for tag in restock['tags']], restock['title'])
                for workspace_name, user_id, reason in failures:
                    report_error(f'Restock notification to user {user_id} in {workspace_name} failed to send due to '
                                 f'{reason}.')

            last_refresh_time = loop_start_time
            failure_count = 0
        except Exception as e:
            report_error(str(e))
            failure_count += 1
            if failure_count >= 5:  # terminate program after 5 consecutive failures
                raise e
        time.sleep(60)