#!/usr/bin/env bash
set -Eeuo pipefail

# The official PostgreSQL image executes this file only when initializing an
# empty data directory. Use psql's identifier quoting instead of interpolating
# the database name into SQL.
KEYCLOAK_DATABASE="${KEYCLOAK_DATABASE:-keycloak}"

psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
    --set=keycloak_database="$KEYCLOAK_DATABASE" <<'SQL'
SELECT format('CREATE DATABASE %I', :'keycloak_database')
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = :'keycloak_database'
)\gexec
SQL
