#!/bin/sh

python manage.py makemigrations
python manage.py migrate

python manage.py collectstatic --noinput
gunicorn apollo_tms.wsgi:application --log-file