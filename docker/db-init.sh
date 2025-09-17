#!/usr/bin/env sh

#db init for fresh deployments

set -e

HOST=${POSTGRES_HOST:-postgres}
USER=${POSTGRES_USER:-videogen}
DB=${POSTGRES_DB:-videogen}
PASS=${POSTGRES_PASSWORD}

export PGPASSWORD="$PASS"

psql -h "$HOST" -U "$USER" -d "$DB" -v ON_ERROR_STOP=1 \
  -f /docker-entrypoint-initdb.d/01_tables.sql \
  -f /docker-entrypoint-initdb.d/03_indexes.sql \
  -f /docker-entrypoint-initdb.d/04_functions.sql

echo "db init ok"

