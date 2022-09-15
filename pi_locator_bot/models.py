# NAME: models.py
# PURPOSE: schema definition for db to keep track of slack users subscribed to 
#          rpi restock notifications
# AUTHOR: Emma Bethel
# CREATED: 8/18/22
# LAST EDITED: 9/14/22

from pi_locator_bot import db


pi_subscription_vendor = db.Table('pi_subscription_to_vendor',
    db.Column('subscription_id', db.Integer, db.ForeignKey('pi_subscription.id')),
    db.Column('vendor_id', db.Integer, db.ForeignKey('pi_vendor.id'))
)


pi_subscription_type = db.Table('pi_subscription_to_type',
    db.Column('subscription_id', db.Integer, db.ForeignKey('pi_subscription.id')),
    db.Column('type_id', db.Integer, db.ForeignKey('pi_type.id'))
)


class Workspace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slack_id = db.Column(db.String(16), nullable=False, unique=True)
    name = db.Column(db.String(64), nullable=False)
    bot_token = db.Column(db.String(64), nullable=False)
    bot_user_id = db.Column(db.String(16), nullable=False)

    subscribers = db.relationship('Subscriber', cascade = "all,delete")


class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slack_id = db.Column(db.String(16), nullable=False)
    workspace = db.Column(db.Integer, db.ForeignKey("workspace.id"), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    subscriptions = db.relationship('PiSubscription', cascade = "all,delete")


class PiSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscriber = db.Column(db.Integer, db.ForeignKey("subscriber.id"), nullable=False)

    vendors = db.relationship('PiVendor', secondary=pi_subscription_vendor)
    types = db.relationship('PiType', secondary=pi_subscription_type)


class PiVendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    param_name = db.Column(db.String(16), nullable=False, unique=True)
    pretty_name = db.Column(db.String(32), nullable=False)
    country = db.Column(db.String(2), nullable=False)

    def __repr__(self) -> str:
        return f'{self.pretty_name} ({self.country})'


class PiType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    param_name = db.Column(db.String(8), nullable=False, unique=True)
    pretty_name = db.Column(db.String(16), nullable=False)

    def __repr__(self) -> str:
        return self.pretty_name
