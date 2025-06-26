#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

cur_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
"$cur_dir/wait_for_db.sh"

# python /app/manage.py compilemessages
python ./manage.py migrate
env DJANGO_DISABLE_SIGNALS=True python ./manage.py loaddata fixtures/groups-and-permissions.json fixtures/dev-environment-and-tests.json
python ./manage.py runserver 0.0.0.0:8000
