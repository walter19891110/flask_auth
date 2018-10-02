#!/bin/sh

gunicorn -c gun.py flask_auth:app
