import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from slackeventsapi import SlackEventAdapter


basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE_NAME = 'rpi_notifier'
DATABASE_USER_NAME = 'slackbot'

app = Flask(__name__)
BASE_URL = os.environ['BASE_URL']

# database setup
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True
}

# prod DB
DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']
app.config['SQLALCHEMY_DATABASE_URI'] =\
    f'mysql://{DATABASE_USER_NAME}:{DATABASE_PASSWORD}@localhost/{DATABASE_NAME}'

# local test DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# slack setup
SLACK_CLIENT_ID = os.environ['SLACK_CLIENT_ID']
SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
SLACK_CLIENT_SECRET = os.environ['SLACK_CLIENT_SECRET']
OAUTH_REDIRECT_URI = f'{BASE_URL}/slack/oauth'

slack_events_adapter = SlackEventAdapter(
    SLACK_SIGNING_SECRET,
    "/slack/chatbot",
    app
)

import pi_locator_bot.models
import pi_locator_bot.views
import pi_locator_bot.commands
