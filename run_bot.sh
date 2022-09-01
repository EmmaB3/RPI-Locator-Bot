#!/bin/bash

trap 'echo TERM signal received; kill "${WEBSERVER_PID}"; kill "${LISTENER_PID}"; wait' TERM

echo "Running rpi locator slackbot with PID $$"

gunicorn -w 4 -b 0.0.0.0 'pi_locator_bot:app'  &
WEBSERVER_PID="$!"

python3 listener.py &
LISTENER_PID="$!"

wait
