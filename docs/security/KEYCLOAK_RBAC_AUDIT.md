# Authentication, RBAC, Ministry Scope, and Audit Operations

## Purpose

This document defines the production authentication and authorization boundary for Congo-Brain. It covers Keycloak authority, realm-role mapping, ministry assignment, registration controls, and operation of the append-only privileged-activity audit log.

## Authentication modes

Congo-Brain supports two mutually exclusive modes.

### Keycloak mode — staging and production

Set:

```env
ENVIRONMENT=production
KEYCLOAK_ENABLED=true
KEYCLOAK_SERVER_URL=https://identity.example.cd
KEYCLOAK_REALM=congo-brain
KEYCLOAK_CLIENT_ID=congo-brain-api
PUBLIC_REGISTRATION_ENABLED=false
```

When `KEYCLOAK_ENABLED=true`:

- Keycloak is the only token authority.
- JWT signatures are validated through the realm JWKS endpoint.
- Issuer and audience are validated.
- A failed Keycloak validation returns HTTP 401.
- Locally signed JWTs are rejected; there is no fallback.
- `/api/v1/auth/login` and `/api/v1/auth/register` return HTTP 404.
- User lifecycle and credential policy are managed in Keycloak.

### Local development mode

Local login is available only when `KEYCLOAK_ENABLED=false`. Public registration is controlled independently by `PUBLIC_REGISTRATION_ENABLED` and defaults to enabled only when `ENVIRONMENT=development`.

Local authentication is a development and test compatibility mode. It must not be enabled in staging or production.

## Keycloak client configuration

Create an OpenID Connect client named `congo-brain-api`:

- Access type: confidential for server-managed flows, or bearer-only when no direct grant is required.
- Access token signing algorithm: RS256.
- Audience: include `congo-brain-api` in access tokens.
- Valid redirect URIs and web origins: restrict to the deployed frontend origins.
- Direct access grants: disabled unless explicitly required by an approved integration.
- Service accounts: disabled unless a machine integration requires one.

Do not place the Keycloak client secret in Git. Inject it through the deployment secret manager.

## Realm roles

Create the following realm roles using the exact lowercase identifiers:

| Realm role | Intended responsibility |
|---|---|
| `admin` | Platform administration and all permissions |
| `national_budget_admin` | National budget, investment, transparency, user provisioning, and audit review |
| `ministry_budget_officer` | Budget and transparency operations for one assigned ministry |
| `project_manager` | Project and investment management and optimization |
| `auditor` | Read-only cross-domain review and audit-log access |
| `executive_viewer` | Cross-domain executive read access |
| `public_viewer` | Approved budget, investment, and transparency read access |

Legacy roles `analyst` and `viewer` remain recognized for compatibility but should not be assigned to new production users.

If a token contains multiple recognized roles, Congo-Brain applies the highest-priority role in this order:

1. `admin`
2. `national_budget_admin`
3. `ministry_budget_officer`
4. `project_manager`
5. `auditor`
6. `executive_viewer`
7. `public_viewer`
8. `analyst`
9. `viewer`

## Ministry claim mapping

A `ministry_budget_officer` must have exactly one ministry assignment. Congo-Brain accepts either:

- a top-level string claim named `ministry`; or
- the first value of the Keycloak user attribute `ministry` exposed under `attributes.ministry`.

Recommended Keycloak protocol mapper:

| Setting | Value |
|---|---|
| Mapper type | User Attribute |
| User attribute | `ministry` |
| Token claim name | `ministry` |
| Claim JSON type | String |
| Add to access token | On |
| Multivalued | Off |

Use the canonical ministry name used by the application data. A ministry officer without a ministry claim receives HTTP 403. A ministry officer requesting, creating, or modifying another ministry's budget or transparency record also receives HTTP 403.

## Registration and administrative provisioning

### Public registration

`PUBLIC_REGISTRATION_ENABLED` controls `/api/v1/auth/register` only in local mode.

- Development default: `true`
- Staging/production default: `false`
- Keycloak mode: endpoint is always unavailable

Public registration never accepts a role field and creates only a non-privileged viewer account.

### Administrative provisioning

In local development mode, authorized administrators can provision users through:

```http
POST /api/v1/auth/users
Authorization: Bearer <admin-token>
```

The caller requires `user:write`. Unknown roles are rejected. A `ministry_budget_officer` without a ministry is rejected. In Keycloak mode, provision users and role mappings in Keycloak instead of creating local credentials.

## Protected interfaces

- Budget, investment, security, transparency, IA GOV, MOEG, GEOS, report exports, and GraphQL require bearer authentication and the corresponding permission.
- GEOS optimization requires `investment:optimize`.
- Decision analysis and scenario/optimization operations require optimization or write permission rather than ordinary read permission.
- GraphQL introspection and the GraphiQL IDE are disabled in staging and production.
- Public citizen-information routes remain intentionally public.

## Privileged-activity audit log

### Recorded fields

Each audit event contains:

- actor subject;
- actor username;
- actor role;
- action;
- resource type and identifier;
- ministry, when applicable;
- structured operation details that exclude credentials and tokens;
- creation time;
- previous event hash;
- SHA-256 event hash.

Events form a hash chain. PostgreSQL append operations use a transaction-scoped advisory lock to prevent concurrent requests from creating branches.

### Immutability controls

Three controls protect the log:

1. The API exposes only a read endpoint; there are no update or delete routes.
2. SQLAlchemy rejects ORM update and delete operations on `AuditEvent`.
3. The PostgreSQL migration creates a trigger that rejects direct database `UPDATE` and `DELETE` operations.

Database superusers can still bypass database controls. Restrict superuser access, forward database logs to an external security system, and export audit events to immutable/WORM storage for high-assurance deployments.

### Reading and validating the log

Authorized administrators and auditors can query:

```http
GET /api/v1/auth/audit-log?limit=100
Authorization: Bearer <token>
```

The caller requires `audit:read`. The response includes `chain_valid`. A value of `false` is a security incident and must trigger investigation; do not repair or delete events in place.

### Audited operation categories

The application records:

- administrative user creation, role/ministry updates, and deletion;
- budget and transaction creation;
- budget anomaly scans;
- transparency-report creation;
- investment creation, portfolio optimization, and scenario comparison;
- security-alert creation and resolution;
- GEOS allocation optimization;
- IA GOV policy, reform, digital-twin, and decision simulations;
- MOEG welfare, investment, NWI, and corruption-scenario analyses.

Authentication failures should be collected by the identity provider and centralized ingress logs; access tokens and passwords must never be written to the application audit log.

## Operational checks

Before authorizing staging or production:

1. Confirm a locally signed token receives HTTP 401 while Keycloak mode is enabled.
2. Confirm every realm role receives only its documented permissions.
3. Confirm ministry officers cannot access a different ministry.
4. Execute one privileged operation and verify its event appears in `/api/v1/auth/audit-log`.
5. Confirm `chain_valid=true`.
6. On PostgreSQL, verify direct update and deletion of an audit row fail with `audit_events is append-only`.
7. Forward application, Keycloak, ingress, and database security logs to centralized monitoring.
8. Alert on repeated HTTP 401/403 responses, invalid audit chains, and failed audit writes.

## Secret-handling rule

Never include passwords, access tokens, refresh tokens, client secrets, private keys, or full authorization headers in audit details, application logs, issue trackers, or documentation.
