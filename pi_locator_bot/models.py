# NAME: models.py
# PURPOSE: schema definition for db to keep track of slack users subscribed to 
#          rpi restock notifications
# AUTHOR: Emma Bethel
# CREATED: 8/18/22
# LAST EDITED: 8/23/22

from pi_locator_bot import db


class Team(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    bot_token = db.Column(db.String(64), nullable=False)
    bot_user_id = db.Column(db.String(16), nullable=False)


class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slack_id = db.Column(db.String(16), nullable=False)
    team = db.ForeignKey("team.id", nullable=False)


class PiSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscriber = db.ForeignKey("subscriber.id")
    team = db.ForeignKey("team.id", nullable=False)


class PiVendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    param_name = db.Column(db.String(16), nullable=False, unique=True)
    pretty_name = db.Column(db.String(16), nullable=False)
    country = db.Column(db.String(2), nullable=False)


class PiType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    param_name = db.Column(db.String(4), nullable=False)
    pretty_name = db.Column(db.String(8), nullable=False)


class PiSubscriptionToVendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor = db.ForeignKey('pi_vendor.id', nullable=False)
    subscription = db.ForeignKey('pi_subscription.id', nullable=False)


class PiSubscriptionToType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.ForeignKey('pi_type.id', nullable=False)
    subscription = db.ForeignKey('pi_subscription.id', nullable=False)
