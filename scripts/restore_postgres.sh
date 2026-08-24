#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

usage() {
    cat <<'EOF'
Usage:
  PG_DSN='postgresql://target-db' BACKUP_FILE=/secure/path/backup.dump \
  CONFIRM_RESTORE=RESTORE scripts/restore_postgres.sh

The script restores only into an empty target and never drops existing objects.

BACKUP_FILE.sha256 is mandatory and is verified before connecting to the database.
PG_DSN must come from a protected environment or secret manager.
EOF
}

require() {
    command -v "$1" >/dev/null 2>&1 || {
        printf 'ERROR: %s is required\n' "$1" >&2
        exit 2
    }
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    usage
    exit 0
fi

: "${PG_DSN:?PG_DSN is required}"
: "${BACKUP_FILE:?BACKUP_FILE is required}"

if [ "${CONFIRM_RESTORE:-}" != "RESTORE" ]; then
    printf 'ERROR: set CONFIRM_RESTORE=RESTORE to authorize this operation\n' >&2
    exit 2
fi
if [ ! -f "$BACKUP_FILE" ]; then
    printf 'ERROR: backup file not found: %s\n' "$BACKUP_FILE" >&2
    exit 2
fi

require pg_restore
require sha256sum
require psql

if [ ! -f "${BACKUP_FILE}.sha256" ]; then
    printf 'ERROR: checksum sidecar not found: %s\n' "${BACKUP_FILE}.sha256" >&2
    exit 2
fi
IFS=' ' read -r expected_hash expected_name extra < "${BACKUP_FILE}.sha256"
case "$expected_hash" in
    *[!0-9a-f]*|'') printf 'ERROR: checksum sidecar contains an invalid SHA-256 value\n' >&2; exit 2 ;;
esac
if [ "${#expected_hash}" -ne 64 ] || [ "$expected_name" != "$(basename "$BACKUP_FILE")" ] || [ -n "${extra:-}" ]; then
    printf 'ERROR: checksum sidecar must contain exactly the selected archive basename\n' >&2
    exit 2
fi
actual_hash=$(sha256sum "$BACKUP_FILE")
actual_hash=${actual_hash%% *}
if [ "$actual_hash" != "$expected_hash" ]; then
    printf 'ERROR: checksum verification failed for %s\n' "$BACKUP_FILE" >&2
    exit 2
fi
printf '%s: OK\n' "$(basename "$BACKUP_FILE")"

pg_restore --list "$BACKUP_FILE" >/dev/null

existing_objects=$(psql "$PG_DSN" -v ON_ERROR_STOP=1 -Atqc \
    "SELECT COUNT(*) FROM pg_catalog.pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema');")
if [ "$existing_objects" != "0" ]; then
    printf 'ERROR: restore target is not empty (%s user table(s)); create a new database\n' "$existing_objects" >&2
    exit 2
fi

restore_args=(
    --dbname="$PG_DSN"
    --no-owner
    --no-privileges
    --exit-on-error
    --single-transaction
)
PGCONNECT_TIMEOUT="${PGCONNECT_TIMEOUT:-15}" pg_restore "${restore_args[@]}" "$BACKUP_FILE"
printf 'Restore completed successfully from %s\n' "$BACKUP_FILE"
