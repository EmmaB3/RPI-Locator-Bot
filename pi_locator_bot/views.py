# NAME: views.py
# PURPOSE: chatbot API endpoint implementation
# AUTHOR: Emma Bethel
# CREATED: 8/22/22
# LAST EDITED: 8/23/22

import logging

from flask import request, make_response
from pi_locator_bot import app

logging.basicConfig(level=logging.DEBUG)


@app.route("/slack/test", methods=["POST"])
def handle_message():
    # TODO: verify... somehow (use this? https://pypi.org/project/slackeventsapi/ not sure how it would work for everything in db though)

    # for verifying endpoint w/ slack (delete later)
    challenge = request.json.get('challenge')
    if challenge is not None:
        make_response(challenge)

    print(request.json)
    return make_response('hello world')
