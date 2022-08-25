# NAME: messages.py
# PURPOSE: utils for mapping user input to prepared responses
# AUTHOR: Emma Bethel
# CREATED: 8/18/22
# LAST EDITED: 8/24/22

import re
from typing import Sequence

from pi_locator_bot import db
from pi_locator_bot.countries import Country
from pi_locator_bot.models import (PiSubscription, PiSubscriptionToType, 
                                   PiSubscriptionToVendor, PiType, PiVendor, 
                                   Subscriber)


# TEAM ID IS DB ID, NOT SLACK ID. COULD DO SAME WITH USER ID?
def handle_message(statement: str, user_id: str, team_id: str) -> str:
    # normalizing string
    word_list = statement.split(' ')
    command = re.sub(r'[^\w\s]', '', word_list[0])
    arguments = []
    for word in word_list[1:]:
        arguments.append(word.lower().strip())

    # matching statement to expected ones
    if command == 'subscribe':
        return subscribe(arguments, user_id, team_id)
    elif command == 'list':
        return list(arguments, user_id, team_id)
    elif command == 'unsubscribe':
        return unsubscribe(arguments, user_id, team_id)
    elif command == 'beep':
        return 'boop'
    else:
        print('STATEMENT', statement)
        return ('Sorry, I didn\'t get that. Use the `help` command to see '
                'available commands and example usage.')


def list(arguments: Sequence[str], user_id: str, team_id: str) -> str:
    if len(arguments) == 0:
        return 'Error: `list` command requires a type.'

    if arguments[0] == 'vendors':
        output = ''
        countries = []
        vendors = PiVendor.query.order_by('country')

        for vendor in vendors:
            country = vendor.country
            if country not in countries:
                countries.append(country)
                output += f'{country}:\n'
            output += f'`{vendor.param_name}` ({vendor.pretty_name})\n'
        return output
    if arguments[0] == 'types':
        types = PiType.query.all()
        output = ''

        for type in types:
           output += f'`{type.param_name}` ({type.pretty_name})\n'
        
        return output
    if arguments[0] == 'subscriptions':
        subscriptions = PiSubscription.query.join(Subscriber).filter_by(slack_id=user_id).filter_by(team=team_id)  # TODO: filter by team as well aaah
        output = ''

        for subscription in subscriptions:
            types = PiType.query.join(PiSubscriptionToType).filter_by(subscription=subscription.id)
            vendors = PiVendor.query.join(PiSubscriptionToVendor).filter_by(subscription=subscription.id)
            type_names, vendor_names = [], []
            for type in types:
                type_names.append(str(type))
            for vendor in vendors:
                vendor_names.append(str(vendor))
            output += f'\u2022 Subscription {subscription.id}: Restock notifications for pi type(s) {", ".join(type_names)} from vendor(s) {", ".join(vendor_names)}\n'
        return output

    return f'Sorry, \'{arguments[0]}\' is not a valid list type.'


def unsubscribe(arguments: Sequence[str], user_id: str, team_id: str) -> str:
    subscriber = Subscriber.query.filter_by(slack_id=user_id).filter_by(team=team_id).first()
    if subscriber is None:
        return f'Sorry, you don\'t have any subscriptions.'

    deleted_ids = []
    for subscription_id in arguments:
        print('HERE', subscription_id)
        try:
            subscription_id = int(subscription_id)
        except ValueError:
            return (f'Sorry, {subscription_id} is not a valid subscription id. You can check the ids of your current '
                    'subscriptions with the `list subscriptions` command.')
        
        subscription = PiSubscription.query.get(subscription_id)

        if subscription is None or subscription.subscriber != subscriber.id:
            return (f'Sorry, {subscription_id} is not one of your subscriptions. You can check the ids of your current '
                    'subscriptions with the `list subscriptions` command.')

        db.session.delete(subscription)
        deleted_ids.append(str(subscription.id))
    
    db.session.commit()
    return f'Successfully deleted subscription(s) {", ".join(deleted_ids)}.'

def subscribe(arguments: Sequence[str], user_id: str, team_id: str) -> str:
    parsed_args = {}
    for arg in arguments:
        split_arg = arg.split('=')
        if len(split_arg) == 2:
            parsed_args[split_arg[0]] = split_arg[1].split(',')

    subscriber = Subscriber.query.filter_by(slack_id=user_id)\
                                 .filter_by(team=team_id).first()
    if subscriber is None:
        subscriber = Subscriber(slack_id=user_id, team=team_id)
        db.session.add(subscriber)
        
    type_params = parsed_args.get('types')
    if type_params is None:
        types = PiType.query.all()
    else:
        types = []
        for type_name in type_params:
            obj = PiType.query.filter_by(param_name=type_name).first()
            if obj is None:
                return f'Error: {type_name} is not a valid pi type.'
            types.append(obj)
    
    region_params = parsed_args.get('regions')
    vendor_params = parsed_args.get('vendors')
    if vendor_params is None:
        if region_params is None:
            vendors = PiVendor.query.all()
        else:
            countries = [country.value for country in Country]
            for region_name in region_params:
                region_name = region_name.upper()
                if region_name not in countries:
                    return f'Error: {region_name} is not a valid region.'

            vendors = PiVendor.query.filter(PiVendor.country.in_(countries))
    else:
        vendors = []
        for vendor_name in vendor_params:  # TODO: this code loooks pretty repetitive (from when you did it with types)... modularize?
            obj = PiVendor.query.filter_by(param_name=vendor_name).first()
            if obj is None:
                return f'Error: {vendor_name} is not a valid pi vendor.'
            vendors.append(obj)

    subscription = PiSubscription(subscriber=subscriber.id)
    db.session.add(subscription)
    db.session.commit()

    vendor_names, type_names = [], []
    for vendor in vendors:
        vendor_names.append(str(vendor))
        db.session.add(
            PiSubscriptionToVendor(
                vendor=vendor.id,
                subscription=subscription.id
            )
        )
    for type in types:
        type_names.append(str(type))
        db.session.add(
            PiSubscriptionToType(
                type=type.id,
                subscription=subscription.id
            )
        )
    db.session.commit()

    return (
        'Now subscribed to restock notifications for pi type(s) '
        f'{", ".join(type_names)} from vendor(s) {", ".join(vendor_names)}.'
    )
