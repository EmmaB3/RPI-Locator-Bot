# NAME: commands.py
# PURPOSE: custom flask cli commands
# AUTHOR: Emma Bethel
# CREATED: 9/27/22

import time
import click
import feedparser
from typing import Mapping, Sequence

from pi_locator_bot import app, db
from pi_locator_bot.monitoring import report_error
from pi_locator_bot.notifier import send_restock_notification
from sqlalchemy.exc import OperationalError


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
            handle_restocks(restocks, last_refresh_time)

            last_refresh_time = loop_start_time
            failure_count = 0
        except Exception as e:
            db.session.rollback()
            report_error(str(e))
            failure_count += 1
            if failure_count >= 5:  # terminate program after 5 consecutive failures
                raise e
        time.sleep(60)


def handle_restocks(restocks: Sequence[Mapping], last_refresh_time: int):
    for restock in restocks:
        if restock['published_parsed'] <= last_refresh_time:
            break
        
        try:
            failures = send_restock_notification([tag['term'] for tag in restock['tags']], restock['title'])
        except OperationalError as e:
            print(e.orig.args)
            if e.orig.args[0] == 2006:  # if db connection went stale, reconnect and try again
                db.session.rollback()
                failures = send_restock_notification([tag['term'] for tag in restock['tags']], restock['title'])
            else:
                raise e

        for workspace_name, user_id, reason in failures:
            report_error(f'Restock notification to user {user_id} in {workspace_name} failed to send due to '
                            f'{reason}.')
