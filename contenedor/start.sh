#!/usr/bin/env bash

cd /code
python manage.py makemigrations
python manage.py migrate

gunicorn --bind :8000 inseguro.wsgi:application --reload
