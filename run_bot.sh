#!/bin/bash

trap 'echo TERM signal received; kill "${WEBSERVER_PID}"; kill "${LISTENER_PID}"; wait' TERM

echo "Running rpi locator slackbot with PID $$"

gunicorn -w 4 'pi_locator_bot:app' &
WEBSERVER_PID="$!"

flask listen-for-restocks &
LISTENER_PID="$!"

wait
