import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from slackeventsapi import SlackEventAdapter

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
BASE_URL = os.environ['BASE_URL']

# database setup
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
