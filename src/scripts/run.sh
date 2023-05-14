#!/bin/bash
set -e

echo "Static files management."
python manage.py collectstatic --noinput
python manage.py compress --force

echo "Build the database."
python manage.py migrate

echo "Serve Django via gunicorn"
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8080 \
  --worker-tmp-dir /dev/shm \
  --workers=2 \
  --capture-output \
  --enable-stdio-inheritance
