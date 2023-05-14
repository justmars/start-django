#!/bin/bash
set -e

echo "Build the database."
python manage.py migrate

echo "Run worker."
python manage.py run_huey
