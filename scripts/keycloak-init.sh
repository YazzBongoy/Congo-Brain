#!/bin/bash
# Keycloak initialization script — creates realm, client, and roles for Congo-Brain.
# Run after Keycloak is healthy: docker exec -it congo-brain-keycloak /opt/keycloak/init.sh

set -euo pipefail

KC_URL="${KEYCLOAK_URL:-http://localhost:8080}"
ADMIN_USER="${KEYCLOAK_ADMIN:-admin}"
ADMIN_PASS="${KEYCLOAK_ADMIN_PASSWORD:-admin_secret_2026}"
REALM="congo-brain"
CLIENT_ID="congo-brain-api"

echo "→ Getting admin token..."
TOKEN=$(curl -s -X POST "$KC_URL/realms/master/protocol/openid-connect/token" \
  -d "client_id=admin-cli" \
  -d "username=$ADMIN_USER" \
  -d "password=$ADMIN_PASS" \
  -d "grant_type=password" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "→ Creating realm: $REALM"
curl -s -X POST "$KC_URL/admin/realms" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"realm\": \"$REALM\",
    \"enabled\": true,
    \"registrationAllowed\": true,
    \"loginWithEmailAllowed\": true,
    \"verifyEmail\": false,
    \"defaultRoles\": [\"viewer\"]
  }" || echo "  (realm may already exist)"

echo "→ Creating client: $CLIENT_ID"
curl -s -X POST "$KC_URL/admin/realms/$REALM/clients" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"clientId\": \"$CLIENT_ID\",
    \"enabled\": true,
    \"publicClient\": false,
    \"secret\": \"congo-brain-api-secret\",
    \"directAccessGrantsEnabled\": true,
    \"serviceAccountsEnabled\": true,
    \"redirectUris\": [\"http://localhost:8000/*\", \"http://localhost:3000/*\"],
    \"webOrigins\": [\"http://localhost:3000\"],
    \"protocol\": \"openid-connect\",
    \"standardFlowEnabled\": true,
    \"implicitFlowEnabled\": false
  }" || echo "  (client may already exist)"

echo "→ Creating roles..."
for ROLE in admin analyst viewer; do
  curl -s -X POST "$KC_URL/admin/realms/$REALM/roles" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$ROLE\", \"description\": \"Role $ROLE\"}" || echo "  (role $ROLE may already exist)"
done

echo "→ Creating test user: admin / admin123"
curl -s -X POST "$KC_URL/admin/realms/$REALM/users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"admin\",
    \"email\": \"admin@congo-brain.com\",
    \"enabled\": true,
    \"emailVerified\": true,
    \"credentials\": [{\"type\": \"password\", \"value\": \"admin123\", \"temporary\": false}]
  }" || echo "  (user may already exist)"

# Assign admin role
USER_ID=$(curl -s "$KC_URL/admin/realms/$REALM/users?username=admin" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")

curl -s -X POST "$KC_URL/admin/realms/$REALM/users/$USER_ID/role-mappings/clients/$(curl -s "$KC_URL/admin/realms/$REALM/clients?clientId=$CLIENT_ID" -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "[{\"name\": \"admin\"}]" || echo "  (role mapping may already exist)"

echo ""
echo "✓ Keycloak initialized for Congo-Brain"
echo "  Realm:    $REALM"
echo "  Client:   $CLIENT_ID"
echo "  Secret:   congo-brain-api-secret"
echo "  User:     admin / admin123"
echo "  Console:  $KC_URL/admin ($ADMIN_USER / $ADMIN_PASS)"
