#!/bin/sh
set -eu

flask --app main db upgrade
flask --app main seed-admin

exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-1}" \
    --timeout 120 \
    main:app
