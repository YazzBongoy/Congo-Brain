#!/usr/bin/env bash
set -u

BASE_URL="${BASE_URL:-}"
ADMIN_TOKEN="${ADMIN_TOKEN:-}"
PG_DSN="${PG_DSN:-}"

failures=0
pass() { printf 'PASS  %s\n' "$1"; }
fail() { printf 'FAIL  %s\n' "$1"; failures=$((failures + 1)); }

require() {
    if ! command -v "$1" >/dev/null 2>&1; then
        printf 'ERROR: %s is required\n' "$1" >&2
        exit 2
    fi
}

usage() {
    cat <<'EOF'
Usage: BASE_URL=https://congo-brain.example.cd [ADMIN_TOKEN=...] [PG_DSN=...] scripts/release_checklist.sh

Automated pre-production checks from docs/security/KEYCLOAK_RBAC_AUDIT.md.
ADMIN_TOKEN enables audit-log verification. PG_DSN (postgres://...) enables
append-only trigger verification.
EOF
}

require jq
require curl

if [ -z "$BASE_URL" ]; then
    usage >&2
    exit 2
fi

code() {
    curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$@"
}

echo "=== Congo-Brain release checklist — ${BASE_URL} ==="

health=$(code "${BASE_URL}/health")
if [ "$health" = "200" ]; then pass "GET /health -> 200"; else fail "GET /health -> ${health} (expected 200)"; fi

anon=$(code "${BASE_URL}/api/v1/geos/provinces")
if [ "$anon" = "401" ]; then pass "protected route without token -> 401"; else fail "protected route without token -> ${anon} (expected 401)"; fi

tampered=$(code -H "Authorization: Bearer eyJhbGciOiJSUzI1NiJ9.tampered.payload" "${BASE_URL}/api/v1/geos/provinces")
if [ "$tampered" = "401" ]; then pass "tampered bearer token -> 401"; else fail "tampered bearer token -> ${tampered} (expected 401)"; fi

login=$(code -X POST -H 'Content-Type: application/json' -d '{}' "${BASE_URL}/api/v1/auth/login")
if [ "${KEYCLOAK_MODE:-0}" = "1" ]; then
    if [ "$login" = "404" ]; then pass "local login disabled under Keycloak mode -> 404"; else fail "local login -> ${login} (expected 404 in Keycloak mode)"; fi
else
    fail "Keycloak production mode is required (set KEYCLOAK_MODE=1)"
fi

register=$(code -X POST -H 'Content-Type: application/json' -d '{}' "${BASE_URL}/api/v1/auth/register")
if [ "$register" = "404" ]; then pass "public registration disabled -> 404"; else fail "/auth/register -> ${register} (expected 404)"; fi

if [ -n "$ADMIN_TOKEN" ]; then
    audit_body=$(mktemp)
    audit_header=$(mktemp)
    chmod 600 "$audit_body" "$audit_header"
    cleanup_audit() { rm -f "$audit_body" "$audit_header"; }
    trap cleanup_audit EXIT INT TERM
    printf 'Authorization: Bearer %s\n' "$ADMIN_TOKEN" > "$audit_header"
    audit_http=$(curl -s -o "$audit_body" -w '%{http_code}' --max-time 15 \
        -H "@$audit_header" \
        "${BASE_URL}/api/v1/auth/audit-log?limit=1")
    if [ "$audit_http" = "200" ]; then
        chain=$(jq -r '.chain_valid // .events[0].chain_valid // empty' "$audit_body" 2>/dev/null)
        if [ "$chain" = "true" ]; then
            pass "audit log readable and chain_valid=true"
        else
            fail "audit chain_valid=${chain:-missing} — treat false as a security incident"
        fi
    else
        fail "GET /api/v1/auth/audit-log -> ${audit_http} (expected 200 with ADMIN_TOKEN)"
    fi
    cleanup_audit
    trap - EXIT INT TERM
else
    fail "audit-log check requires ADMIN_TOKEN"
fi

if [ -n "$PG_DSN" ] && command -v psql >/dev/null 2>&1; then
    # Inspect the exact enabled trigger definitions instead of inferring success
    # from a failing destructive statement. This works even when the table is empty
    # and distinguishes a database/schema failure from an enforced security control.
    trigger_sql=$(cat <<'SQL'
SELECT COUNT(*)
FROM pg_trigger t
JOIN pg_class c ON c.oid = t.tgrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_proc p ON p.oid = t.tgfoid
WHERE n.nspname = current_schema()
  AND c.relname = 'audit_events'
  AND NOT t.tgisinternal
  AND t.tgenabled IN ('O', 'A')
  AND p.proname = 'prevent_audit_event_mutation'
  AND regexp_replace(p.prosrc, '\s+', ' ', 'g') ~ '^ *BEGIN RAISE EXCEPTION ''audit_events is append-only''; END; *$'
  AND (
    (t.tgname = 'audit_events_immutable' AND t.tgtype = 27)
    OR
    (t.tgname = 'audit_events_no_truncate' AND t.tgtype = 34)
  );
SQL
    )
    if ! trigger_count=$(PGCONNECT_TIMEOUT="${PGCONNECT_TIMEOUT:-15}" \
        psql "$PG_DSN" -X -v ON_ERROR_STOP=1 -Atqc "$trigger_sql" 2>&1); then
        fail "cannot verify append-only controls: PostgreSQL connection/schema query failed"
    elif [ "$trigger_count" = "2" ]; then
        pass "append-only audit triggers are present, enabled and correctly scoped"
    else
        fail "append-only audit triggers invalid: expected 2 exact enabled definitions, found ${trigger_count:-0}"
    fi
else
    fail "append-only trigger check requires PG_DSN and psql"
fi

cat <<'EOF'

--- Manual items (docs/security/KEYCLOAK_RBAC_AUDIT.md) ---
[ ] Each realm role receives only its documented permissions
[ ] A ministry_budget_officer cannot access another ministry's records
[ ] One privileged operation appears in the audit log
[ ] Application, Keycloak, ingress and database logs forwarded to centralized monitoring
[ ] Alerts on repeated 401/403, invalid audit chains and failed audit writes

EOF

if [ "${MANUAL_CHECKS_CONFIRMED:-}" != "YES" ]; then
    fail "manual release checks are not confirmed (set MANUAL_CHECKS_CONFIRMED=YES after sign-off)"
fi

printf 'Result: %s failure(s)\n' "$failures"
[ "$failures" -eq 0 ] && exit 0
exit 1
