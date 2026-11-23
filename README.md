# Congo-Brain

Plateforme d'IA de gouvernance pour la République Démocratique du Congo — **Government Economic Optimization System (GEOS)**

Congo-Brain est un moteur d'intelligence artificielle qui optimise les décisions publiques en maximisant le Surplus National Net (SNN) de la RDC. Il combine économique du bien-être, recherche opérationnelle et intelligence artificielle dans un seul système unifié.

## Formule centrale

```
max SNN = CS + PS + GR + NRV − DWL − EC
```

| Composante | Signification | Source |
|---|---|---|
| **CS** | Consumer Surplus — surplus des consommateurs | Services publics (WTP − prix − coûts indirects) |
| **PS** | Producer Surplus — surplus des producteurs | Entreprises (revenus − coûts totaux) |
| **GR** | Government Revenue — recettes publiques nettes | Impôts, douanes, minières |
| **NRV** | Natural Resource Value — valeur des ressources naturelles | Mines (production × valeur + transformation locale) |
| **DWL** | Deadweight Loss — pertes d'efficacité | Corruption, évasion fiscale, contrats anomiques |
| **EC** | Environmental Cost — coûts environnementaux | Exploitation minière, pollution |

## Architecture

```
Congo-Brain
├── congo_brain/
│   ├── api/
│   │   ├── server.py                          # FastAPI application
│   │   └── v1/
│   │       ├── auth.py                        # Inscription, connexion JWT
│   │       ├── geos.py                        # GEOS — 14 entités + SNN
│   │       ├── ia_gov.py                      # IA GOV — 8 modules
│   │       ├── economic.py                    # MOEG / moteur économique
│   │       ├── budget.py                      # Budgets publics
│   │       ├── citizen.py                     # Services citoyens
│   │       ├── investment.py                  # Investissements
│   │       ├── transparency.py                # Transparence
│   │       ├── security.py                    # Sécurité
│   │       └── router.py                      # Assembleur de routes
│   ├── core/
│   │   ├── config.py                          # Configuration (SECRET_KEY, DATABASE_URL)
│   │   ├── database.py                        # SQLAlchemy engine + sessions
│   │   ├── rbac.py                            # Contrôle d'accès basé sur les rôles
│   │   └── security.py                        # Hachage bcrypt + JWT
│   ├── models/
│   │   ├── user.py                            # Utilisateurs (admin, analyst, viewer)
│   │   ├── geos/
│   │   │   └── entities.py                    # 14 entités GEOS
│   │   ├── budget.py, citizen.py, investment.py, transparency.py
│   │   └── security_alert.py
│   ├── schemas/                               # Pydantic schemas
│   ├── services/
│   │   ├── ia_gov/                            # 8 modules IA GOV
│   │   │   ├── resource_optimizer.py          # Module 1 — optimiseur SNN
│   │   │   ├── consumer_surplus.py            # Module 2 — CS
│   │   │   ├── producer_surplus.py            # Module 3 — PS
│   │   │   ├── national_resource.py           # Module 4 — ressources
│   │   │   ├── governance_score.py            # Module 5 — gouvernance
│   │   │   ├── corruption_detector.py         # Module 6 — corruption
│   │   │   ├── digital_twin.py                # Module 7 — jumeau numérique
│   │   │   ├── decision_ai.py                 # Module 8 — IA décisionnelle
│   │   │   ├── snn_engine.py                  # Moteur SNN unifié (14 entités)
│   │   │   └── collectors.py                  # Collecteurs de données
│   │   ├── economic/                          # MOEG
│   │   │   ├── welfare_model.py               # SNN sectoriel
│   │   │   ├── resource_optimizer.py          # Chaîne de valeur (7 ressources)
│   │   │   ├── investment_allocator.py        # LP/MILP + scoring NSB
│   │   │   ├── nwi.py                         # Indicateur de bien-être national
│   │   │   └── corruption_calculator.py       # DWL + coûts environnementaux
│   │   └── ai/                                # IA avancée
│   │       ├── anomaly_detector.py            # Détection d'anomalies
│   │       ├── investment_optimizer.py        # Optimiseur LP/MILP
│   │       └── risk_analyzer.py               # Analyse de risques
│   └── cli/                                   # CLI Typer
├── tests/                                     # 305 tests
│   ├── test_ia_gov.py                         # 52 tests IA GOV
│   ├── test_economic_engine.py                # 45 tests MOEG
│   ├── test_geos.py                           # 41 tests GEOS
│   ├── test_predictor.py                      # 23 tests prédictions ML
│   ├── test_auth_api.py                       # 22 tests auth/RBAC
│   ├── test_graphql.py                        # 17 tests GraphQL
│   ├── test_audit_log.py                      # 15 tests audit inviolable
│   ├── test_ministry_authorization.py         # cloisonnement ministère
│   ├── test_reports.py                        # exports PDF/Excel
│   └── test_security.py                       # 10 tests sécurité
├── alembic/                                   # Migrations DB
└── docs/iagov/                                # Documentation architecture
```

## 14 entités GEOS

| Entité | Description | Alimente |
|---|---|---|
| `Province` | 26 provinces officielles (découpage 2015) + rattachement aux 11 provinces historiques | Dashboard |
| `Citizen` | Citoyens avec revenus, éducation, satisfaction | CS |
| `Company` | Entreprises (Gécamines, SNEL, Vodacom) | PS, DWL |
| `Ministry` | 10 ministères avec scores de gouvernance | GR, Dashboard |
| `Budget` | Budgets alloués/exécutés par ministère | GR |
| `Resource` | 8 mines (Kamoa-Kakula, Tenke Fungurume, Kibali Gold...) | NRV, EC |
| `Tax` | 4 types (IS, TVA, Douanes, Minières) | GR, DWL |
| `Project` | Projets avec impact SNN estimé | Optimisation |
| `Infrastructure` | Routes, hôpitaux, écoles, réseaux | Dashboard |
| `PublicService` | 8 services (électricité, eau, santé...) | CS |
| `Contract` | Marchés publics avec scores d'anomalie | DWL |
| `Payment` | Paiements vérifiés / flaggés | DWL |
| `Market` | Marchés par secteur | PS |
| `Indicator` | Indicateurs de suivi | Dashboard |

## 8 modules IA GOV

| # | Module | Fonction |
|---|---|---|
| 1 | **ResourceOptimizationEngine** | Optimisation SNN sous contraintes, simulation de politiques publiques |
| 2 | **ConsumerSurplusEngine** | Calcul CS par service public, ranking, simulation d'améliorations |
| 3 | **ProducerSurplusEngine** | Calcul PS par entreprise, réformes fiscales, drag de corruption |
| 4 | **NationalResourceEngine** | Suivi des mines, valeur brute/ajoutée/fiscale, scénarios de transformation |
| 5 | **GovernanceScoreEngine** | Score = 40%Opt + 20%Trans + 20%Perf + 20%Sat, cibles d'amélioration |
| 6 | **CorruptionDetectionEngine** | 8 types d'anomalies, scoring de risque, résumé par secteur |
| 7 | **NationalDigitalTwin** | Jumeau numérique des 26 provinces, simulation d'investissements |
| 8 | **DecisionAI** | Questions en langage naturel → allocations SNN recommandées |

## API

### GEOS — `/api/v1/geos/`

```
GET  /dashboard                    # Vue complète avec SNN agrégé
GET  /snn                          # Détail CS+PS+GR+NRV-DWL-EC
POST /optimize                     # Allocation budgétaire optimale
GET  /provinces                    # Liste des provinces
GET  /provinces/{name}             # Détail province
GET  /companies                    # Liste des entreprises
GET  /companies/{name}             # Détail entreprise
GET  /companies/ps/total           # PS total entreprises
GET  /ministries                   # Liste des ministères
GET  /ministries/{name}            # Détail ministère
GET  /ministries/ranking           # Classement par gouvernance
GET  /resources                    # Liste des ressources
GET  /resources/{name}             # Détail ressource
GET  /resources/nrv/total          # NRV total
GET  /resources/ec/total           # EC total
GET  /taxes                        # Liste des impôts
GET  /taxes/revenue/total          # GR total
GET  /projects                     # Liste des projets
GET  /projects/snn/total           # Impact SNN total
GET  /public-services              # Liste des services publics
GET  /public-services/cs/total     # CS total
GET  /contracts                    # Liste des contrats
GET  /payments                     # Liste des paiements
GET  /markets                      # Liste des marchés
GET  /indicators                   # Liste des indicateurs
```

### IA GOV — `/api/v1/ia-gov/`

```
GET  /dashboard                    # Vue complète des 8 modules
GET  /optimizer                    # Moteur SNN + contraintes
POST /optimizer/simulate           # Simulation de politiques
GET  /consumer-surplus             # CS services publics
GET  /consumer-surplus/ranking     # Classement CS
GET  /producer-surplus             # PS entreprises
GET  /producer-surplus/ranking     # Classement PS
POST /producer-surplus/simulate-reform  # Simulation réformes
GET  /resources                    # Mines nationales
GET  /resources/mineral/{type}     # Par type de minéral
GET  /governance                   # Scores ministères
GET  /governance/ranking           # Classement gouvernance
GET  /corruption                   # Anomalies détectées
GET  /corruption/risk-summary      # Résumé des risques
GET  /twin                         # Jumeau numérique
POST /twin/simulate                # Simulation investissements
POST /twin/compare                 # Comparaison provinces
GET  /decision                     # IA décisionnelle
POST /decision/ask                 # Question en langage naturel
```

### MOEG — `/api/v1/economic/`

```
GET  /welfare                      # SNN sectoriel
GET  /resources                    # Chaîne de valeur (7 ressources)
GET  /investments                  # Allocation LP/MILP + NSB
GET  /nwi                          # Indicateur de bien-être national
GET  /corruption                   # DWL + coûts environnementaux
GET  /dashboard                    # Tableau de bord économique
```

### Auth — `/api/v1/auth/`

```
POST /register                     # Inscription
POST /login                        # Connexion (JWT)
GET  /me                           # Profil utilisateur
GET  /users                        # Liste utilisateurs (admin)
PUT  /users/{id}/role              # Modifier rôle (admin)
DELETE /users/{id}                 # Supprimer (admin)
GET  /roles                        # Liste des rôles
```

## Technologies

- **Python 3.11+**
- **FastAPI** — API REST asynchrone
- **SQLAlchemy 2.x** — ORM avec migrations Alembic
- **PostgreSQL 16** — base de données
- **Keycloak 24** — gestion des identités et authentification SSO
- **bcrypt** — hachage des mots de passe
- **python-jose** — tokens JWT
- **scipy** — optimisation LP/MILP (greedy fallback)
- **Docker + Docker Compose** — conteneurisation
- **GitHub Actions** — CI/CD (tests + build Docker)
- **Typer + Rich** — CLI
- **slowapi** — rate limiting
- **pytest** — 179 tests

## Installation

### Développement local

```bash
git clone https://github.com/YazzBongoy/Congo-Brain.git
cd Congo-Brain
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Éditer .env avec vos paramètres
```

### Docker (recommandé)

```bash
git clone https://github.com/YazzBongoy/Congo-Brain.git
cd Congo-Brain
docker compose up -d
```

Cela lance :
- **PostgreSQL** sur `localhost:5432`
- **Keycloak** sur `localhost:8080` (admin / admin_secret_2026)
- **Congo-Brain API** sur `localhost:8000`

Initialiser Keycloak :

```bash
docker exec -it congo-brain-keycloak bash /opt/keycloak/init.sh
```

## Utilisation

### API

```bash
# Sans Docker
uvicorn congo_brain.api.server:app --reload

# Avec Docker
docker compose up app
# → http://localhost:8000/docs (Swagger UI)
# → http://localhost:8000/health (Health check)
```

### CLI

```bash
congo-brain --help
```

### Tests

```bash
pytest tests/ -v
# 305 passed
```

### Keycloak (SSO)

Quand `KEYCLOAK_ENABLED=true` :
- L'authentification utilise les tokens Keycloak (RS256, JWKS)
- Les rôles Keycloak (admin, analyst, viewer)映射 vers les rôles internes
- Fallback sur JWT local si Keycloak est désactivé

Console d'administration : `http://localhost:8080/admin`

## Modèle de données

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Province   │────<│   Citizen   │     │  Contract   │
│             │────<│             │     │     │       │
│             │────<│   Company   │────<│     │       │
│             │────<│             │     │  Payment    │
│             │────<│Infrastructure│    └─────────────┘
│             │────<│             │
│             │────<│PublicService│
└──────┬──────┘     └─────────────┘
       │
       │         ┌─────────────┐     ┌─────────────┐
       │         │  Ministry   │────<│   Budget    │
       │         │             │     └─────────────┘
       │         │             │────<│   Project   │
       │         └─────────────┘     └─────────────┘
       │
       │         ┌─────────────┐     ┌─────────────┐
       └────────>│  Resource   │     │    Tax      │
                 └─────────────┘     └─────────────┘
                       │
                 ┌─────┴──────┐
                 │   Market   │
                 └────────────┘
                       │
                 ┌─────┴──────┐
                 │ Indicator  │
                 └────────────┘
```

## Roadmap

- [x] Phase 0 — Sécurité (bcrypt, JWT, RBAC, Alembic)
- [x] Phase 1 — PostgreSQL, user management, rate limiting
- [x] MOEG — Moteur économique (SNN, NWI, allocation LP/MILP)
- [x] IA GOV — 8 modules (optimisation, CS, PS, ressources, gouvernance, corruption, jumeau numérique, IA décisionnelle)
- [x] GEOS — 14 entités + moteur SNN unifié
- [x] Phase 2 — Docker Compose, Keycloak SSO, CI/CD GitHub Actions
- [x] Phase 3 — React UI dashboard, monitoring Prometheus/Grafana
- [x] Phase 4 — Kubernetes, Helm charts
- [x] Phase 5 — Données réelles RDC, modèle prédictif ML
- [x] Options — Exports PDF/Excel, API GraphQL (Strawberry)
- [x] Workstream 1 — Auth & Audit : Keycloak-first, RBAC 9 rôles, cloisonnement ministère, audit inviolable (hash-chain) — voir [docs/security/KEYCLOAK_RBAC_AUDIT.md](docs/security/KEYCLOAK_RBAC_AUDIT.md)
- [ ] Workstream 2 — Socle release : migrations à jour, docs synchronisées, staging Render/Helm, checklist pré-production, backups
- [ ] Workstream 3+ — Observabilité & alerting, données RDC 2026, frontend multi-rôles

## Licence

MIT — Voir [LICENSE](LICENSE)
