#!/bin/bash
echo "Starting deployment script..."
echo "Running migrations..."
python migrate.py
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "Starting Daphne server..."
daphne interview_platform.asgi:application --port $PORT --bind 0.0.0.0
python manage.py runserver 0.0.0.0:$PORT 