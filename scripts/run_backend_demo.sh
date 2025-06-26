#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python /app/manage.py collectstatic --noinput
python ./manage.py migrate
env DJANGO_DISABLE_SIGNALS=True python ./manage.py loaddata fixtures/groups-and-permissions.json fixtures/demo-environment-data.json
/usr/local/bin/gunicorn property_management.wsgi --workers 3 --threads 3 --bind 0.0.0.0:8000 --chdir=/app
