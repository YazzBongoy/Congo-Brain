#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

usage() {
    cat <<'EOF'
Usage: PG_DSN='service=congo-brain-backup' [BACKUP_DIR=./backups] [BACKUP_NAME=congo_brain] scripts/backup_postgres.sh

Creates a PostgreSQL custom-format backup, validates its catalogue, and writes
a SHA-256 sidecar. Run it separately with BACKUP_NAME=keycloak for Keycloak.
PG_DSN must come from a protected environment or secret manager, never source control.
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
BACKUP_DIR="${BACKUP_DIR:-./backups}"
BACKUP_NAME="${BACKUP_NAME:-congo_brain}"

case "$BACKUP_NAME" in
    ''|*[!A-Za-z0-9_-]*)
        printf 'ERROR: BACKUP_NAME may contain only letters, digits, underscore and hyphen\n' >&2
        exit 2
        ;;
esac

require pg_dump
require pg_restore
require sha256sum


mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_path="${BACKUP_DIR%/}/${BACKUP_NAME}-${timestamp}.dump"
temporary_path="$(mktemp "${BACKUP_DIR%/}/.${BACKUP_NAME}-${timestamp}.XXXXXX")"
cleanup() { rm -f "$temporary_path"; }
trap cleanup EXIT INT TERM

PGCONNECT_TIMEOUT="${PGCONNECT_TIMEOUT:-15}" pg_dump \
    --dbname="$PG_DSN" \
    --format=custom \
    --no-owner \
    --no-privileges \
    --file="$temporary_path"

pg_restore --list "$temporary_path" >/dev/null
mv "$temporary_path" "$backup_path"
(
    cd "$(dirname "$backup_path")"
    sha256sum "$(basename "$backup_path")" > "$(basename "${backup_path}.sha256")"
)

printf 'Backup verified: %s\n' "$backup_path"
printf 'Checksum: %s\n' "${backup_path}.sha256"
