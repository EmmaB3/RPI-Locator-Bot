# NAME: views.py
# PURPOSE: chatbot API endpoint implementation
# AUTHOR: Emma Bethel
# CREATED: 8/22/22
# LAST EDITED: 9/14/22

import logging

from flask import make_response, request, render_template
from pi_locator_bot import app, db, slack_events_adapter, OAUTH_REDIRECT_URI, SLACK_CLIENT_ID, SLACK_CLIENT_SECRET
from pi_locator_bot.messages import handle_message
from pi_locator_bot.models import Workspace
from pi_locator_bot.monitoring import report_error
from slack_sdk import WebClient
from sqlalchemy.exc import IntegrityError

logging.basicConfig(level=logging.DEBUG)


@slack_events_adapter.on("message")
def respond_to_dm(payload):
    workspace = Workspace.query.filter_by(slack_id=payload['team_id']).first()

    user_slack_id = payload['event']['user']

    # if message is a DM and didn't come from the bot itself, respond to it
    if user_slack_id != workspace.bot_user_id and payload['event']['channel_type'] == 'im':
        message_text = payload['event']['text']
        slack_client = WebClient(token=workspace.bot_token)

        try:
            response_text = handle_message(message_text, user_slack_id, workspace.id)
        except Exception as e:
            response_text = 'Sorry, an error has occured. Developers will be notified.'
            report_error(str(e))

        slack_client.chat_postMessage(
            channel=user_slack_id,
            text=response_text
        )

    return make_response()


@slack_events_adapter.on('app_uninstalled')
def delete_workspace(payload):
    workspace = Workspace.query.filter_by(slack_id=payload['team_id']).first()
    db.session.delete(workspace)
    db.session.commit()

    return make_response()


@app.route('/', methods=['GET'])
def show_homepage():
    return render_template('index.html', url=OAUTH_REDIRECT_URI)

@app.route('/slack/oauth', methods=['GET'])
def ouath_callback():
    code = request.args.get('code')
    if code is not None:
        client = WebClient()

        oauth_response = client.oauth_v2_access(
            client_id=SLACK_CLIENT_ID,
            client_secret=SLACK_CLIENT_SECRET,
            redirect_uri=OAUTH_REDIRECT_URI,
            code=code
        )

        if oauth_response['ok']:
            workspace_name = oauth_response['team']['name']
            workspace_id = oauth_response['team']['id']
            bot_user_id = oauth_response['bot_user_id']
            bot_token = oauth_response['access_token']

            try:
                db.session.add(Workspace(slack_id=workspace_id, name=workspace_name, bot_token=bot_token, bot_user_id=bot_user_id))
                db.session.commit()
                return make_response('Success', 201)
            except IntegrityError:
                return make_response('Error: Bot has already been added to this workspace.', 400)
    return make_response('Authentication Failed', 401)
