#!/bin/bash

python backend/manage.py migrate --noinput

gunicorn backend.ficrec.wsgi:application --bind 127.0.0.1:8000 &

nginx -g "daemon off;"