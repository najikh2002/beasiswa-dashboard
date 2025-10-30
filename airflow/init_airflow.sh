#!/bin/bash
set -e

if [ "$1" = "webserver" ]; then
    airflow db init
    airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com \
        --password admin || true
fi

exec airflow "$@"