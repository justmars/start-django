#!/bin/bash
set -e

echo "Setup debugger"
pip install --upgrade pip
pip install debugpy

echo "Static files management."
python manage.py collectstatic --noinput
python manage.py compress --force

echo "Build the database."
python manage.py migrate

echo "Serve Django via runserver"
python -m debugpy \
  --wait-for-client \
  --listen 0.0.0.0:5678 \
  manage.py runserver 0.0.0.0:8080 --nothreading --noreload
