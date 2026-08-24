#!/usr/bin/env bash
# Secure and reconciling Keycloak bootstrap for Congo-Brain.

set -Eeuo pipefail
umask 077

KC_URL="${KEYCLOAK_URL:-${KEYCLOAK_SERVER_URL:-http://localhost:8080}}"
ENVIRONMENT="${ENVIRONMENT:-development}"
if [ "$ENVIRONMENT" = production ] || [ "$ENVIRONMENT" = staging ]; then
    python3 - "$KC_URL" <<'PY'
import sys
from urllib.parse import urlsplit

parsed = urlsplit(sys.argv[1])
if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
    raise SystemExit("ERROR: production/staging Keycloak URL must be an absolute HTTPS URL without userinfo")
PY
fi
ADMIN_USER="${KEYCLOAK_ADMIN:-admin}"
ADMIN_PASS="${KEYCLOAK_ADMIN_PASSWORD:?KEYCLOAK_ADMIN_PASSWORD is required}"
REALM="${KEYCLOAK_REALM:-congo-brain}"
CLIENT_ID="${KEYCLOAK_CLIENT_ID:-congo-brain-api}"
CLIENT_SECRET="${KEYCLOAK_CLIENT_SECRET:?KEYCLOAK_CLIENT_SECRET is required}"
FRONTEND_URL="${KEYCLOAK_FRONTEND_URL:-http://localhost:3000}"
API_URL="${KEYCLOAK_API_URL:-http://localhost:8000}"
DIRECT_GRANTS_ENABLED="${KEYCLOAK_DIRECT_GRANTS_ENABLED:-false}"
case "$DIRECT_GRANTS_ENABLED" in true|false) ;; *) printf 'ERROR: KEYCLOAK_DIRECT_GRANTS_ENABLED must be true or false\n' >&2; exit 2 ;; esac
export ADMIN_USER ADMIN_PASS REALM CLIENT_ID CLIENT_SECRET FRONTEND_URL API_URL DIRECT_GRANTS_ENABLED

temporary_dir=$(mktemp -d)
cleanup() { rm -rf "$temporary_dir"; }
trap cleanup EXIT INT TERM

urlencode() {
    python3 -c 'import sys,urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$1"
}

write_payload() {
    printf '%s' "$1" > "$temporary_dir/payload.json"
    chmod 600 "$temporary_dir/payload.json"
}

request() {
    local method=$1 path=$2 output=${3:-$temporary_dir/response.json} code
    shift 3 || true
    code=$(curl --silent --show-error -o "$output" -w '%{http_code}' \
        -X "$method" -H "@$temporary_dir/auth.header" "$@" "$KC_URL$path")
    case "$code" in
        200|201|204) return 0 ;;
        *) printf 'ERROR: Keycloak %s %s returned HTTP %s\n' "$method" "$path" "$code" >&2; return 1 ;;
    esac
}

post_allow_conflict() {
    local path=$1 payload=$2 label=$3 code
    write_payload "$payload"
    code=$(curl --silent --show-error -o "$temporary_dir/response.json" -w '%{http_code}' \
        -X POST -H "@$temporary_dir/auth.header" -H 'Content-Type: application/json' \
        --data-binary "@$temporary_dir/payload.json" "$KC_URL$path")
    case "$code" in
        201|204) printf '✓ %s created\n' "$label" ;;
        409) printf '• %s exists; reconciling it\n' "$label" ;;
        *) printf 'ERROR: Keycloak returned HTTP %s while creating %s\n' "$code" "$label" >&2; return 1 ;;
    esac
}

echo "→ Authenticating the Keycloak administrator..."
TOKEN=$(
    python3 -c 'import os,sys,urllib.parse; sys.stdout.write(urllib.parse.urlencode({"client_id":"admin-cli","username":os.environ["ADMIN_USER"],"password":os.environ["ADMIN_PASS"],"grant_type":"password"}))' \
    | curl --fail --silent --show-error \
        -H 'Content-Type: application/x-www-form-urlencoded' --data-binary @- \
        "$KC_URL/realms/master/protocol/openid-connect/token" \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])'
)
printf 'Authorization: Bearer %s\n' "$TOKEN" > "$temporary_dir/auth.header"
chmod 600 "$temporary_dir/auth.header"
unset TOKEN ADMIN_PASS

realm_payload=$(python3 -c 'import json,os; print(json.dumps({"realm":os.environ["REALM"],"enabled":True,"registrationAllowed":False,"loginWithEmailAllowed":True,"verifyEmail":True}))')
post_allow_conflict "/admin/realms" "$realm_payload" "realm $REALM"
write_payload "$realm_payload"
request PUT "/admin/realms/$(urlencode "$REALM")" "$temporary_dir/response.json" \
    -H 'Content-Type: application/json' --data-binary "@$temporary_dir/payload.json"
request GET "/admin/realms/$(urlencode "$REALM")" "$temporary_dir/realm.json"
python3 - "$temporary_dir/realm.json" <<'PY'
import json, sys
realm = json.load(open(sys.argv[1], encoding="utf-8"))
assert realm.get("enabled") is True
assert realm.get("registrationAllowed") is False
assert realm.get("loginWithEmailAllowed") is True
assert realm.get("verifyEmail") is True
assert realm.get("defaultRole", {}).get("id")
PY
printf '✓ realm security settings reconciled and verified\n'

client_payload=$(python3 -c 'import json,os; print(json.dumps({"clientId":os.environ["CLIENT_ID"],"enabled":True,"publicClient":False,"secret":os.environ["CLIENT_SECRET"],"directAccessGrantsEnabled":os.environ["DIRECT_GRANTS_ENABLED"]=="true","serviceAccountsEnabled":False,"redirectUris":[os.environ["API_URL"]+"/*",os.environ["FRONTEND_URL"]+"/*"],"webOrigins":[os.environ["FRONTEND_URL"]],"protocol":"openid-connect","standardFlowEnabled":True,"implicitFlowEnabled":False}))')
post_allow_conflict "/admin/realms/$(urlencode "$REALM")/clients" "$client_payload" "client $CLIENT_ID"
request GET "/admin/realms/$(urlencode "$REALM")/clients?clientId=$(urlencode "$CLIENT_ID")" "$temporary_dir/clients.json"
client_uuid=$(python3 - "$temporary_dir/clients.json" "$CLIENT_ID" <<'PY'
import json, sys
clients = [item for item in json.load(open(sys.argv[1], encoding="utf-8")) if item.get("clientId") == sys.argv[2]]
if len(clients) != 1:
    raise SystemExit(f"expected exactly one client, found {len(clients)}")
print(clients[0]["id"])
PY
)
write_payload "$client_payload"
request PUT "/admin/realms/$(urlencode "$REALM")/clients/$(urlencode "$client_uuid")" "$temporary_dir/response.json" \
    -H 'Content-Type: application/json' --data-binary "@$temporary_dir/payload.json"
request GET "/admin/realms/$(urlencode "$REALM")/clients/$(urlencode "$client_uuid")" "$temporary_dir/client.json"
python3 - "$temporary_dir/client.json" "$API_URL" "$FRONTEND_URL" "$DIRECT_GRANTS_ENABLED" <<'PY'
import json, sys
client = json.load(open(sys.argv[1], encoding="utf-8"))
assert client.get("enabled") is True
assert client.get("publicClient") is False
assert client.get("directAccessGrantsEnabled") is (sys.argv[4] == "true")
assert client.get("serviceAccountsEnabled") is False
assert client.get("standardFlowEnabled") is True
assert client.get("implicitFlowEnabled") is False
assert client.get("protocol") == "openid-connect"
assert sorted(client.get("redirectUris", [])) == sorted([sys.argv[2] + "/*", sys.argv[3] + "/*"])
assert client.get("webOrigins") == [sys.argv[3]]
PY
request GET "/admin/realms/$(urlencode "$REALM")/clients/$(urlencode "$client_uuid")/client-secret" "$temporary_dir/client-secret.json"
python3 - "$temporary_dir/client-secret.json" <<'PY'
import json, os, sys
stored = json.load(open(sys.argv[1], encoding="utf-8")).get("value")
assert stored and stored == os.environ["CLIENT_SECRET"]
PY
printf '✓ client security settings and secret reconciled\n'

audience_payload=$(python3 -c 'import json,os; print(json.dumps({"name":"congo-brain-api-audience","protocol":"openid-connect","protocolMapper":"oidc-audience-mapper","config":{"included.client.audience":os.environ["CLIENT_ID"],"id.token.claim":"false","access.token.claim":"true"}}))')
request GET "/admin/realms/$(urlencode "$REALM")/clients/$(urlencode "$client_uuid")/protocol-mappers/models" \
    "$temporary_dir/protocol-mappers.json"
audience_mapper_id=$(python3 - "$temporary_dir/protocol-mappers.json" <<'PY'
import json, sys
matches = [mapper for mapper in json.load(open(sys.argv[1], encoding="utf-8")) if mapper.get("name") == "congo-brain-api-audience"]
if len(matches) > 1:
    raise SystemExit("multiple Congo-Brain audience mappers found")
if matches:
    print(matches[0]["id"])
PY
)
write_payload "$audience_payload"
if [ -n "$audience_mapper_id" ]; then
    request DELETE "/admin/realms/$(urlencode "$REALM")/clients/$(urlencode "$client_uuid")/protocol-mappers/models/$(urlencode "$audience_mapper_id")" \
        "$temporary_dir/response.json"
fi
request POST "/admin/realms/$(urlencode "$REALM")/clients/$(urlencode "$client_uuid")/protocol-mappers/models" \
    "$temporary_dir/response.json" -H 'Content-Type: application/json' \
    --data-binary "@$temporary_dir/payload.json"
request GET "/admin/realms/$(urlencode "$REALM")/clients/$(urlencode "$client_uuid")/protocol-mappers/models" \
    "$temporary_dir/protocol-mappers.json"
python3 - "$temporary_dir/protocol-mappers.json" "$CLIENT_ID" <<'PY'
import json, sys
matches = [mapper for mapper in json.load(open(sys.argv[1], encoding="utf-8")) if mapper.get("name") == "congo-brain-api-audience"]
assert len(matches) == 1
mapper = matches[0]
assert mapper.get("protocol") == "openid-connect"
assert mapper.get("protocolMapper") == "oidc-audience-mapper"
config = mapper.get("config", {})
assert config.get("included.client.audience") == sys.argv[2]
assert config.get("access.token.claim") == "true"
assert config.get("id.token.claim") == "false"
PY
printf '✓ client audience mapper reconciled and verified\n'
unset CLIENT_SECRET client_payload audience_payload

mapfile -t application_roles < <(
    python3 -c 'from congo_brain.core.rbac import Role; print("\n".join(role.value for role in Role))'
)
test "${#application_roles[@]}" -gt 0
for role in "${application_roles[@]}"; do
    role_payload=$(python3 -c 'import json,sys; print(json.dumps({"name":sys.argv[1],"description":"Congo-Brain role "+sys.argv[1]}))' "$role")
    post_allow_conflict "/admin/realms/$(urlencode "$REALM")/roles" "$role_payload" "role $role"
done

# Keep public_viewer as a leaf role, then reject direct or nested application-role
# drift through any wrapper assigned to Keycloak's generated default composite.
request GET "/admin/realms/$(urlencode "$REALM")/roles/public_viewer" "$temporary_dir/public-viewer-role.json"
public_viewer_id=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["id"])' \
    "$temporary_dir/public-viewer-role.json")
request GET "/admin/realms/$(urlencode "$REALM")/roles-by-id/$(urlencode "$public_viewer_id")/composites" \
    "$temporary_dir/public-viewer-composites.json"
public_viewer_composite_count=$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1], encoding="utf-8"))))' \
    "$temporary_dir/public-viewer-composites.json")
if [ "$public_viewer_composite_count" -gt 0 ]; then
    request DELETE "/admin/realms/$(urlencode "$REALM")/roles-by-id/$(urlencode "$public_viewer_id")/composites" \
        "$temporary_dir/response.json" -H 'Content-Type: application/json' \
        --data-binary "@$temporary_dir/public-viewer-composites.json"
fi

request GET "/admin/realms/$(urlencode "$REALM")" "$temporary_dir/realm.json"
default_role_id=$(python3 - "$temporary_dir/realm.json" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["defaultRole"]["id"])
PY
)
request GET "/admin/realms/$(urlencode "$REALM")/roles-by-id/$(urlencode "$default_role_id")/composites" \
    "$temporary_dir/default-composites-before.json"
python3 - "$temporary_dir/public-viewer-role.json" "$temporary_dir/default-composite.json" \
    "$temporary_dir/remove-default-composites.json" <<'PY'
import json, sys
public_viewer = json.load(open(sys.argv[1], encoding="utf-8"))
with open(sys.argv[2], "w", encoding="utf-8") as output:
    json.dump([public_viewer], output)
with open(sys.argv[3], "w", encoding="utf-8") as output:
    json.dump([], output)
PY
chmod 600 "$temporary_dir/default-composite.json" "$temporary_dir/remove-default-composites.json"
python3 - "$temporary_dir/default-composites-before.json" <<'PY' > "$temporary_dir/default-composite-roles.tsv"
import json, sys
for role in json.load(open(sys.argv[1], encoding="utf-8")):
    print(f'{role["id"]}\t{role["name"]}')
PY
while IFS=$'\t' read -r direct_role_id direct_role_name; do
    [ -n "$direct_role_id" ] || continue
    closure_file="$temporary_dir/closure-$(printf '%s' "$direct_role_id" | tr -cd 'A-Za-z0-9_-').json"
    request GET "/admin/realms/$(urlencode "$REALM")/roles-by-id/$(urlencode "$direct_role_id")/composites/realm" \
        "$closure_file"
    python3 - "$temporary_dir/default-composites-before.json" "$temporary_dir/remove-default-composites.json" \
        "$closure_file" "$direct_role_id" "$direct_role_name" <<'PY'
import json, sys
from congo_brain.core.rbac import Role

current = json.load(open(sys.argv[1], encoding="utf-8"))
remove = json.load(open(sys.argv[2], encoding="utf-8"))
closure = {role.get("name") for role in json.load(open(sys.argv[3], encoding="utf-8"))}
role_id, role_name = sys.argv[4], sys.argv[5]
forbidden = {role.value for role in Role} - {"public_viewer"}
if role_name in forbidden or closure & forbidden:
    remove.append(next(role for role in current if role.get("id") == role_id))
with open(sys.argv[2], "w", encoding="utf-8") as output:
    json.dump(remove, output)
PY
done < "$temporary_dir/default-composite-roles.tsv"
remove_count=$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1], encoding="utf-8"))))' \
    "$temporary_dir/remove-default-composites.json")
if [ "$remove_count" -gt 0 ]; then
    request DELETE "/admin/realms/$(urlencode "$REALM")/roles-by-id/$(urlencode "$default_role_id")/composites" \
        "$temporary_dir/response.json" -H 'Content-Type: application/json' \
        --data-binary "@$temporary_dir/remove-default-composites.json"
fi
request POST "/admin/realms/$(urlencode "$REALM")/roles-by-id/$(urlencode "$default_role_id")/composites" \
    "$temporary_dir/response.json" -H 'Content-Type: application/json' \
    --data-binary "@$temporary_dir/default-composite.json"
request GET "/admin/realms/$(urlencode "$REALM")/roles-by-id/$(urlencode "$default_role_id")/composites/realm" \
    "$temporary_dir/default-effective-composites.json"
python3 - "$temporary_dir/default-effective-composites.json" <<'PY'
import json, sys
from congo_brain.core.rbac import Role

application_roles = {role.value for role in Role}
effective = {role.get("name") for role in json.load(open(sys.argv[1], encoding="utf-8"))}
assert effective & application_roles == {"public_viewer"}
PY
printf '✓ least-privileged default public_viewer role reconciled and verified recursively\n'

# The historical bootstrap created a known realm-local admin/admin123 account.
# Never silently keep or delete it: fail closed unless deletion was explicitly approved.
request GET "/admin/realms/$(urlencode "$REALM")/users?username=admin&exact=true" "$temporary_dir/legacy-users.json"
legacy_ids=$(python3 - "$temporary_dir/legacy-users.json" <<'PY'
import json, sys
for user in json.load(open(sys.argv[1], encoding="utf-8")):
    if user.get("username") == "admin":
        print(user["id"])
PY
)
if [ -n "$legacy_ids" ]; then
    if [ "${CONFIRM_REMOVE_LEGACY_ADMIN:-}" != "REMOVE" ]; then
        printf 'ERROR: legacy realm user admin exists; set CONFIRM_REMOVE_LEGACY_ADMIN=REMOVE after approval\n' >&2
        exit 3
    fi
    while IFS= read -r legacy_id; do
        request DELETE "/admin/realms/$(urlencode "$REALM")/users/$(urlencode "$legacy_id")" "$temporary_dir/response.json"
    done <<< "$legacy_ids"
    printf '✓ legacy realm-local admin account removed\n'
fi

printf '✓ Keycloak bootstrap completed: realm=%s client=%s\n' "$REALM" "$CLIENT_ID"
printf '  Public registration and direct grants are disabled; provision users through an approved workflow.\n'
