# NAME: messages.py
# PURPOSE: utils for mapping user input to prepared responses
# AUTHOR: Emma Bethel
# CREATED: 8/18/22
# LAST EDITED: 8/24/22

import re
from typing import Sequence

from pi_locator_bot import basedir, db
from pi_locator_bot.countries import Country
from pi_locator_bot.models import PiSubscription, PiType, PiVendor, Subscriber


# WORKSPACE ID IS DB ID, NOT SLACK ID
def handle_message(statement: str, user_slack_id: str, workspace_id: str) -> str:
    # normalizing string
    word_list = statement.split(' ')
    command = re.sub(r'[^\w\s]', '', word_list[0])
    command = command.lower()
    arguments = []
    for word in word_list[1:]:
        arguments.append(word.lower().strip())

    # matching statement to expected ones
    if command == 'subscribe':
        return subscribe(arguments, user_slack_id, workspace_id)
    elif command == 'list':
        return show_list(arguments, user_slack_id, workspace_id)
    elif command == 'unsubscribe':
        return unsubscribe(arguments, user_slack_id, workspace_id)
    elif command in ('help', 'about', 'tips'):
        return read_response_from_file(command)
    elif command == 'beep':
        return 'boop'
    else:
        return ('Sorry, I didn\'t get that. Use the `help` command to see '
                'available commands and example usage.')


# FILE NAME SHOULD NOT INCLUDE .TXT
def read_response_from_file(file_name: str):
    response_file = open(f'{basedir}/responses/{file_name}.txt')
    response = response_file.read()
    response_file.close()

    return response


def show_list(arguments: Sequence[str], user_slack_id: str, workspace_id: str) -> str:
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
        subscriptions = PiSubscription.query.join(Subscriber).filter_by(slack_id=user_slack_id).filter_by(workspace=workspace_id)

        output = ''
        for subscription in subscriptions:
            types = subscription.types
            vendors = subscription.vendors
            type_names, vendor_names = [], []
            for type in types:
                type_names.append(str(type))
            for vendor in vendors:
                vendor_names.append(str(vendor))
            output += f'\u2022 Subscription {subscription.id}: Restock notifications for pi type(s) {", ".join(type_names)} from vendor(s) {", ".join(vendor_names)}\n'
        
        if output == '':
            return ('You are not subscribed to any restock notifications at this time. Use the `subscribe` command to '
                    'change that!')
        return output

    return f'Sorry, \'{arguments[0]}\' is not a valid list type.'


def unsubscribe(arguments: Sequence[str], user_slack_id: str, workspace_id: str) -> str:
    error_message = ('Sorry, {subscription} is not one of your subscriptions. You can check the ids of your '
                     'current subscriptions with the `list subscriptions` command.')
    subscriber = Subscriber.query.filter_by(slack_id=user_slack_id).filter_by(workspace=workspace_id).first()
    if subscriber is None:
        return 'You do not have any subscriptions at this time. Try creating some with the `subscription` command!'

    deleted_ids = []
    for subscription_id in arguments:
        try:
            subscription_id = int(subscription_id)
        except ValueError:
            return error_message.format(subscription=subscription_id)
        
        subscription = PiSubscription.query.get(subscription_id)

        if subscription is None or subscription.subscriber != subscriber.id:
            return error_message.format(subscription=subscription_id)

        db.session.delete(subscription)
        deleted_ids.append(str(subscription.id))
    
    db.session.commit()
    return f'Successfully deleted subscription(s) {", ".join(deleted_ids)}.'

def subscribe(arguments: Sequence[str], user_slack_id: str, workspace_id: str) -> str:
    parsed_args = {}
    for arg in arguments:
        split_arg = arg.split('=')
        if len(split_arg) == 2:
            parsed_args[split_arg[0]] = split_arg[1].split(',')

    subscriber = Subscriber.query.filter_by(slack_id=user_slack_id)\
                                 .filter_by(workspace=workspace_id).first()
    if subscriber is None:
        subscriber = Subscriber(slack_id=user_slack_id, workspace=workspace_id)
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
            all_countries = [country.value for country in Country]
            countries = []
            for region_name in region_params:
                region_name = region_name.upper()
                if region_name not in all_countries:
                    return f'Error: {region_name} is not a valid region.'
                else:
                    countries.append(region_name)
            vendors = list(PiVendor.query.filter(PiVendor.country.in_(countries)))

    else:
        vendors = []
        for vendor_name in vendor_params:  # TODO: this code loooks pretty repetitive (from when you did it with types)... modularize?
            obj = PiVendor.query.filter_by(param_name=vendor_name).first()
            if obj is None:
                return f'Error: {vendor_name} is not a valid pi vendor.'
            vendors.append(obj)

    subscription = PiSubscription(subscriber=subscriber.id, vendors=vendors, types=types)
    db.session.add(subscription)
    db.session.commit()

    vendor_names, type_names = [], []
    for vendor in vendors:
        vendor_names.append(str(vendor))

    for type in types:
        type_names.append(str(type))

    return (
        'Now subscribed to restock notifications for pi type(s) '
        f'{", ".join(type_names)} from vendor(s) {", ".join(vendor_names)}.'
    )
