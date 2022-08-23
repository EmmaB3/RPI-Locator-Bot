# NAME: countries.py
# PURPOSE: country enum definition (for use in rpi vendor definitions)
# AUTHOR: Emma Bethel
# CREATED: 8/20/22
# LAST EDITED: 8/20/22

from enum import Enum, unique


@unique
class Country(Enum):
    UNITED_STATES = 'US'
    UNITED_KINGDOM = 'UK'
    AUSTRIA = 'AT'
    BELGIUM = 'BE'
    CANADA = 'CA'
    CHINA = 'CN'
    FRANCE = 'FR'
    GERMANY = 'DE'
    ITALY = 'IT'
    JAPAN = 'JP'
    NETHERLANDS = 'NL'
    POLAND = 'PL'
    PORTUGAL = 'PT'
    SOUTH_AFRICA = 'ZA'
    SPAIN = 'ES'
    SWEDEN = 'SE'
    SWITZERLAND = 'CH'
