# NAME: create_vendors_and_types.py
# PURPOSE: quickstart script for filling the database with vendors and types
# AUTHOR: Emma Bethel
# CREATED: 8/24/22
# LAST EDITED: 8/24/22

from pi_locator_bot import db
from pi_locator_bot.countries import Country
from pi_locator_bot.models import PiType, PiVendor

VENDORS = [
    (
        Country.UNITED_STATES, [
            ('Adafruit', 'adafruit'),
            ('Chicago Electronic Distributors', 'chicagodist'),
            ('Digi-Key', 'digikeyus'),
            ('Newark', 'newark'),
            ('OKDO', 'okdous'),
            ('Pishop', 'pishopus'),
            ('Sparkfun', 'sparkfun'),
            ('Vilros', 'vilros')
        ]
    ),
    (
        Country.UNITED_KINGDOM, [
            ('Farnell', 'farnell')
        ]
    )
]

TYPES = [
    ('CM3', 'cm3'),
    ('CM4', 'cm4'),
    ('Pi 3', 'pi3'), 
    ('Pi 4', 'pi4'),
    ('Pi Zero', 'pizero')
]


if __name__ == '__main__':
    for pretty_name, param_name in TYPES:
        db.session.add(PiType(pretty_name=pretty_name, param_name=param_name))
    
    for country, vendors in VENDORS:
        for pretty_name, param_name in vendors:
            db.session.add(PiVendor(country=country.value, pretty_name=pretty_name, param_name=param_name))
        
    db.session.commit()
