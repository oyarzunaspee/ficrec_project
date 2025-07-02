#!/bin/bash
service nginx start
cd /app
exec gunicorn ficrec.wsgi:application --bind 127.0.0.1:8000 --workers 1
