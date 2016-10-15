#!/usr/bin/env bash

./manage.py migrate && ./manage.py collectstatic --no-input && mod_wsgi-docker-start