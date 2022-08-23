# NAME: messages.py
# PURPOSE: utils for mapping user input to prepared responses
# AUTHOR: Emma Bethel
# CREATED: 8/18/22
# LAST EDITED: 8/20/22

import re


def get_response_message(statement: str, *args, **kwargs) -> str:
    # normalizing string
    statement = statement.lower().strip()
    statement = re.sub(r'[^\w\s]', '', statement)

    # matching statement to expected ones
    if statement == 'beep':
        return 'boop'
    else:
        return ('Sorry, I didn\'t get that. Use the `help` command to see '
                'available commands and example usage.')

