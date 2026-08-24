# Roadmap — GEOS / IAGov

## Phase 0 — Fondations ✅ (commit e411b92)
- bcrypt + JWT auth
- CI/CD GitHub Actions
- Alembic migrations
- 35 tests

## Phase 1a — RBAC & Sécurité ✅ (commit 914158f)
- PostgreSQL migration
- 3 rôles (admin, analyst, viewer)
- User management CRUD
- Rate limiting
- 42 tests

## Phase 1b — IA Améliorée ✅ (commit 180ad76)
- Anomaly detector (corruption)
- Investment optimizer LP/MILP
- Risk analyzer
- 75 tests

## Phase MOEG — Moteur Économique ✅ (commit 16bf331)
- Welfare model, Resource optimizer, Investment allocator
- NWI (National Welfare Index)
- Corruption calculator
- 75 tests

## Phase SNN — Modèle Central ✅ (commit de143a1)
- SNN = CS + PS + GR + NRV - DWL - EC
- 87 tests

## Phase IA GOV — 8 Modules ✅ (commit d43e314)
- 8 modules IA: Resource, CS, PS, NRV, Governance, Corruption, Twin, Decision
- 139 tests

## Phase GEOS — 14 Entités ✅ (commit 0b389ae)
- 14 tables SQLAlchemy
- SNNOptimizationEngine
- GEOS API (22 endpoints)
- 179 tests

## Phase Docker & Keycloak ✅ (commit 294f3aa)
- Dockerfile + docker-compose (6 services)
- Keycloak JWKS JWT validation
- CI/CD Docker build + GHCR
- 179 tests

## Phase Frontend React ✅ (commit 534cf6e)
- Vite + React 18 + TypeScript + Chart.js
- 6 pages: Dashboard, Provinces, Ministries, Resources, Companies, Projects
- Dark theme, responsive
- Docker nginx proxy

## Phase Données Réelles ✅ (commit e1323af)
- 8 provinces, 8 entreprises, 8 mines, 6 impôts
- 8 ministères, 8 services, 8 projets
- Sources: Banque Mondiale, PNUD, UNESCO

## Phase Prédiction ML ✅ (commit 41524e4)
- PredictiveModel avec Monte Carlo
- 7 scénarios (baseline → pessimiste)
- Intervalles de confiance 5%-95%
- 202 tests

## Phase Monitoring — Prometheus/Grafana ✅ (commit 45d3049)
- Prometheus + Grafana
- Métriques HTTP, latence, erreurs
- SNN gauge
- Dashboard Grafana provisionné

## Option 5 — Helm/Kubernetes ✅ (commit bc2dd29)
- Helm charts, Ingress, ConfigMaps, Secrets
- Values staging/production

## Option 6 — Export Rapports ✅ (commit 73c5770)
- PDF (fpdf2) / Excel (openpyxl)
- Rapports budget et optimisation

## Option 7 — GraphQL ✅ (commit b77ee62)
- Strawberry GraphQL, schéma entités complet

## Workstream 1 — Auth & Audit ✅ (commits bfaed01 → e3d652b)
- Auth Keycloak-first (RS256/JWKS), fallback local dev uniquement
- RBAC 9 rôles hiérarchisés + cloisonnement ministère (`ministry_budget_officer`)
- Journal d'audit inviolable : hash-chain SHA-256, écritures transactionnelles fail-closed
- Triggers PostgreSQL anti-UPDATE/DELETE/TRUNCATE sur audit_events
- ~305 tests ; doc d'exploitation : docs/security/KEYCLOAK_RBAC_AUDIT.md

## Workstream 2 — Socle Release (EN COURS)
- [x] Migration a93d8e71c4b2 (users.role String(64)) committée, round-trip SQLite+PG vérifié
- [ ] Resynchronisation README / ROADMAP avec l'état réel
- [ ] Durcissement render.yaml + checklist release exécutable
- [ ] Externalisation des secrets Helm
- [ ] Runbook backup/restore PostgreSQL
