import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from slackeventsapi import SlackEventAdapter

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# database setup
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# slack setup
slack_events_adapter = SlackEventAdapter(
    os.environ['SLACK_SIGNING_SECRET'],
    "/slack/test",
    app
)

import pi_locator_bot.models
import pi_locator_bot.views
