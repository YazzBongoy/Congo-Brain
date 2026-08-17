# Congo-Brain — Proposition Plan

## Executive Summary

Congo-Brain is a Governance-by-AI platform for the Democratic Republic of the Congo. The project has a solid prototype (Phase 0) with a working FastAPI monolith, SQLite database, CLI, citizen web UI, and AI analysis algorithms seeded with real 2025 DRC government budget data. This plan proposes a phased roadmap to evolve it into a production-grade, secure, and scalable platform aligned with the 5 open GitHub issues and the IAGov architecture documents.

---

## Phase 0 — Stabilize & Secure (Current Sprint)

**Goal:** Fix critical issues in the existing codebase before adding features.

| # | Task | Priority | Details |
|---|------|----------|---------|
| 0.1 | Replace SHA-256 password hashing with bcrypt/argon2 | Critical | `congo_brain/core/security.py` uses raw SHA-256 — insecure. Switch to `passlib[bcrypt]` or `argon2-cffi`. |
| 0.2 | Enforce JWT authentication on protected routes | Critical | Add `Depends(get_current_user)` middleware to budget, investment, transparency, and security endpoints. Keep citizen services public. |
| 0.3 | Remove or deprecate `ia_gov/` package | High | It duplicates `congo_brain` citizen services with in-memory data. Archive or delete. |
| 0.4 | Fix CI pipeline (`ci.yml`) | High | Replace `pip install markdownlint-cli` with `npm install -g markdownlint-cli`. |
| 0.5 | Add Alembic for database migrations | High | Initialize Alembic, generate initial migration, replace `db init`/`db reset` with `alembic upgrade`/`alembic downgrade`. |
| 0.6 | Fix SQLAlchemy 2.x compatibility | Medium | `cli/app.py:58` — wrap raw SQL in `text()`. Fix global state mutation in `anomaly_detector.py`. |
| 0.7 | Add environment validation | Medium | Validate `SECRET_KEY != "change-me-in-production"` at startup. Fail loudly if not set. |
| 0.8 | Write foundational tests | High | Unit tests for AI engines (anomaly detector, optimizer, risk analyzer), service layer, and API endpoints. Target: core modules covered. |

**Deliverable:** A secure, tested, CI-passing monolith ready for feature development.

---

## Phase 1 — Core Features & Data Quality

**Goal:** Complete the MVP feature set and improve data integrity.

| # | Task | Priority | Details |
|---|------|----------|---------|
| 1.1 | PostgreSQL migration | High | Switch from SQLite to PostgreSQL 15. Update `DATABASE_URL`, Dockerfile, and `render.yaml`. Use TimescaleDB extension for time-series budget data. |
| 1.2 | Role-based access control (RBAC) | High | Implement `admin`, `analyst`, `viewer` roles. Admins manage users/budgets, analysts run AI tools, viewers read data. |
| 1.3 | Budget anomaly detection improvements | Medium | Add streaming anomaly detection (not just batch). Add email/webhook alerts for high-severity anomalies. |
| 1.4 | Investment optimizer enhancements | Medium | Replace greedy algorithm with LP/MILP solver (HiGHS). Add scenario comparison UI. |
| 1.5 | Transparency dashboard API | Medium | Add `/api/v1/transparency/dashboard` with per-ministry compliance scores, trend data, and audit findings. |
| 1.6 | Expand citizen services data | Medium | Add more procedures, contacts, rights, and FAQ from real DRC government sources. |
| 1.7 | API documentation | Medium | Add OpenAPI descriptions, example requests/responses, and error codes for all endpoints. |
| 1.8 | Rate limiting & CORS | Medium | Add `slowapi` rate limiting and proper CORS configuration for production. |

**Deliverable:** Production-ready MVP with PostgreSQL, RBAC, enhanced AI, and comprehensive API docs.

---

## Phase 2 — React UI & Microservices Foundation

**Goal:** Build the React SPA and begin microservices decomposition (GitHub Issues #5, #8, #9).

| # | Task | Priority | Details |
|---|------|----------|---------|
| 2.1 | React 18 + Tailwind SPA | High | Replace vanilla JS SPA with React. Pages: Dashboard, Budgets, Investments, Security, Transparency, Citizen Services, Admin. (Issue #8) |
| 2.2 | Keycloak authentication | High | Deploy Keycloak for SSO. Replace JWT self-issuance with Keycloak-backed auth. (Issue #8) |
| 2.3 | Spring Boot Budget Service | High | Extract budget module into a standalone Java 21 Spring Boot microservice with JUnit 5 and Testcontainers. (Issue #5) |
| 2.4 | Docker Compose for local dev | High | Multi-service `docker-compose.yml`: FastAPI core, Spring Boot budget, PostgreSQL, Keycloak, Redis (caching). (Issue #9) |
| 2.5 | API Gateway (Kong/Envoy) | Medium | Route requests to appropriate microservices. Handle auth, rate limiting, and request transformation at the gateway. |
| 2.6 | Event bus (Apache Kafka) | Medium | Publish budget updates, security alerts, and anomaly events to Kafka topics. Consumers update downstream services. |
| 2.7 | KPI Dashboard | Medium | Real-time KPIs: total budget, spending vs. revenue, anomaly count, investment ROI, risk scores. WebSocket updates. |
| 2.8 | Helm charts for K8s | Medium | Helm charts for each microservice. Support staging/production environments. (Issue #9) |

**Deliverable:** Multi-service architecture with React UI, Keycloak auth, and Kubernetes-ready deployment.

---

## Phase 3 — AI Engine & Economic Engine

**Goal:** Build the advanced AI and economic analysis capabilities (GitHub Issues #6, #7).

| # | Task | Priority | Details |
|---|------|----------|---------|
| 3.1 | Economic Engine service | High | FastAPI service implementing the Surplus National Net (SNN) model. LP/MILP optimization with HiGHS/CBC solvers. Monte-Carlo simulation for scenario analysis. (Issue #6) |
| 3.2 | LLM-powered AI Engine | High | FastAPI service with Claude API integration, RAG pipeline (FAISS vector store), policy document Q&A, corruption detection via gradient-boosted trees. (Issue #7) |
| 3.3 | Time-series forecasting | High | Prophet/XGBoost models for budget trend prediction, revenue forecasting, and expenditure projections. (Issue #7) |
| 3.4 | Digital Twin simulation | Medium | Mesa agent-based model for economic policy simulation. Test budget allocation scenarios before real-world implementation. |
| 3.5 | Anomaly detection ML upgrade | Medium | Replace rule-based detection with gradient-boosted trees (XGBoost/LightGBM) trained on historical anomaly data. |
| 3.6 | AI model versioning & registry | Medium | MLflow or similar for tracking model versions, metrics, and deployments. |
| 3.7 | Model monitoring | Medium | Track prediction drift, feature drift, and model performance degradation over time. |

**Deliverable:** Full AI/Economic engine with LLM integration, forecasting, and optimization solvers.

---

## Phase 4 — Observability, Hardening & Launch

**Goal:** Production hardening, monitoring, and official launch preparation.

| # | Task | Priority | Details |
|---|------|----------|---------|
| 4.1 | Observability stack | High | Prometheus metrics, Grafana dashboards, structured logging (JSON), distributed tracing (OpenTelemetry). |
| 4.2 | Security audit | High | Penetration testing, OWASP Top 10 review, secrets management (Vault), dependency vulnerability scanning. |
| 4.3 | Performance testing | High | Load testing with Locust/k6. Target: 1000 concurrent users, <200ms p95 API latency. |
| 4.4 | Backup & disaster recovery | High | Automated PostgreSQL backups, point-in-time recovery, multi-AZ deployment on Render/K8s. |
| 4.5 | Compliance & data governance | Medium | Data retention policies, audit logging, GDPR-like data handling for citizen information. |
| 4.6 | Mobile app (PWA or React Native) | Medium | Offline-capable PWA for citizen services. Push notifications for security alerts. |
| 4.7 | Documentation site | Medium | MkDocs or Docusaurus site with API reference, architecture diagrams, and user guides. |
| 4.8 | Beta launch | High | Invite-only beta for government analysts and civil society organizations. Feedback collection pipeline. |

**Deliverable:** Production-grade platform ready for public launch.

---

## Architecture Evolution Summary

```
Phase 0-1:                          Phase 2-4:
+-------------------+              +-------------------+
|   FastAPI Monolith |              |   Kong API Gateway |
|   + SQLite/PG      |   ------>   |   + Keycloak Auth  |
|   + CLI            |              +--------+----------+
|   + Vanilla SPA    |                       |
+-------------------+              +--------v----------+
                                   | Microservices       |
                                   | - FastAPI Core      |
                                   | - Spring Boot Budget|
                                   | - AI Engine (LLM)   |
                                   | - Economic Engine   |
                                   +--------+-----------+
                                            |
                                   +--------v-----------+
                                   | Kafka Event Bus    |
                                   +--------+-----------+
                                            |
                                   +--------v-----------+
                                   | PostgreSQL + Redis  |
                                   | TimescaleDB + FAISS |
                                   +--------------------+
```

---

## Quick Wins (Do Immediately)

1. **Fix password hashing** — `pip install passlib[bcrypt]`, replace SHA-256 in `security.py`
2. **Add route protection** — One decorator on protected endpoints
3. **Fix CI** — Change one line in `ci.yml`
4. **Delete `ia_gov/`** — Remove redundant code
5. **Add 5-10 tests** — Cover anomaly detector, optimizer, and auth endpoints

These 5 changes would dramatically improve the project's security, reliability, and code quality with minimal effort.

---

## Resource Estimates

| Phase | Duration | Team Size | Key Skills |
|-------|----------|-----------|------------|
| Phase 0 | 1-2 weeks | 1-2 | Python, Security, Testing |
| Phase 1 | 4-6 weeks | 2-3 | Python, PostgreSQL, API Design |
| Phase 2 | 8-12 weeks | 3-5 | React, Java, DevOps, K8s |
| Phase 3 | 10-16 weeks | 3-5 | ML/AI, Python, Optimization |
| Phase 4 | 4-8 weeks | 2-3 | DevOps, Security, QA |

---

*Plan prepared for YazzBongoy / Congo-Brain project — August 2026*
