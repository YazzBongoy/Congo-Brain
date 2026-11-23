#!/usr/bin/env bash
set -Eeuo pipefail

: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${KEYCLOAK_DB_NAME:?KEYCLOAK_DB_NAME is required}"
: "${KEYCLOAK_DB_USER:?KEYCLOAK_DB_USER is required}"
: "${KEYCLOAK_DB_PASSWORD:?KEYCLOAK_DB_PASSWORD is required}"

psql --set=ON_ERROR_STOP=1 \
    --username "$POSTGRES_USER" \
    --dbname "$POSTGRES_DB" \
    --set=kc_db="$KEYCLOAK_DB_NAME" \
    --set=kc_user="$KEYCLOAK_DB_USER" \
    --set=kc_password="$KEYCLOAK_DB_PASSWORD" <<'SQL'
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'kc_user', :'kc_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'kc_user')
\gexec

SELECT format('CREATE DATABASE %I OWNER %I', :'kc_db', :'kc_user')
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :'kc_db')
\gexec
SQL
