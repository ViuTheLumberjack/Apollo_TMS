#!/bin/sh

python manage.py makemigrations
python manage.py migrate

python manage.py collectstatic --noinput
/root/.local/bin/gunicorn apollo_tms.wsgi:application --bind=0.0.0.0:8000 --workers=4