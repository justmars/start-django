#!/bin/bash
set -e

# Swap workers like https://www.joseferben.com/posts/django-on-flyio/
# Fly offers 3 instances with 256MB of memory for free. It’s possible to run Django on 256MB with 2 Gunicorn workers and swap enabled. Without a swap file, workers run out of memory and crash every now and then.

echo "Static files management."
python manage.py collectstatic --noinput
python manage.py compress --force

echo "Build the database."
python manage.py migrate

echo "Serve Django via gunicorn"
gunicorn config.wsgi:application \
  --bind 0.0.0.0:$PORT \
  --worker-tmp-dir /dev/shm \
  --workers=2 \
  --capture-output \
  --enable-stdio-inheritance && python manage.py run_huey
