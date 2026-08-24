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
[ "$health" = "200" ] && pass "GET /health -> 200" || fail "GET /health -> ${health} (expected 200)"

anon=$(code "${BASE_URL}/api/v1/geos/provinces")
[ "$anon" = "401" ] && pass "protected route without token -> 401" || fail "protected route without token -> ${anon} (expected 401)"

tampered=$(code -H "Authorization: Bearer eyJhbGciOiJSUzI1NiJ9.tampered.payload" "${BASE_URL}/api/v1/geos/provinces")
[ "$tampered" = "401" ] && pass "tampered bearer token -> 401" || fail "tampered bearer token -> ${tampered} (expected 401)"

login=$(code -X POST -H 'Content-Type: application/json' -d '{}' "${BASE_URL}/api/v1/auth/login")
if [ "${KEYCLOAK_MODE:-0}" = "1" ]; then
    [ "$login" = "404" ] && pass "local login disabled under Keycloak mode -> 404" || fail "local login -> ${login} (expected 404 in Keycloak mode)"
else
    echo "SKIP  local-login-disabled check (set KEYCLOAK_MODE=1 for staging/production)"
fi

register=$(code -X POST -H 'Content-Type: application/json' -d '{}' "${BASE_URL}/api/v1/auth/register")
[ "$register" = "404" ] && pass "public registration disabled -> 404" || echo "WARN  /auth/register -> ${register} (verify PUBLIC_REGISTRATION_ENABLED=false)"

if [ -n "$ADMIN_TOKEN" ]; then
    audit_http=$(curl -s -o /tmp/cb_audit.$$ -w '%{http_code}' --max-time 15 \
        -H "Authorization: Bearer ${ADMIN_TOKEN}" \
        "${BASE_URL}/api/v1/auth/audit-log?limit=1")
    if [ "$audit_http" = "200" ]; then
        chain=$(jq -r '.chain_valid // .events[0].chain_valid // empty' /tmp/cb_audit.$$ 2>/dev/null)
        if [ "$chain" = "true" ]; then
            pass "audit log readable and chain_valid=true"
        else
            fail "audit chain_valid=${chain:-missing} — treat false as a security incident"
        fi
    else
        fail "GET /api/v1/auth/audit-log -> ${audit_http} (expected 200 with ADMIN_TOKEN)"
    fi
    rm -f /tmp/cb_audit.$$
else
    echo "SKIP  audit-log check (set ADMIN_TOKEN to enable)"
fi

if [ -n "$PG_DSN" ] && command -v psql >/dev/null 2>&1; then
    for stmt in "UPDATE audit_events SET action='x'" "DELETE FROM audit_events" "TRUNCATE audit_events"; do
        if psql "$PG_DSN" -v ON_ERROR_STOP=1 -qc "$stmt" >/dev/null 2>&1; then
            fail "append-only violated: ${stmt%% *}"
        else
            pass "append-only enforced: ${stmt%% *}"
        fi
    done
else
    echo "SKIP  append-only trigger check (set PG_DSN and install psql to enable)"
fi

cat <<'EOF'

--- Manual items (docs/security/KEYCLOAK_RBAC_AUDIT.md) ---
[ ] Each realm role receives only its documented permissions
[ ] A ministry_budget_officer cannot access another ministry's records
[ ] One privileged operation appears in the audit log
[ ] Application, Keycloak, ingress and database logs forwarded to centralized monitoring
[ ] Alerts on repeated 401/403, invalid audit chains and failed audit writes

EOF

printf 'Result: %s failure(s)\n' "$failures"
[ "$failures" -eq 0 ] && exit 0
exit 1
