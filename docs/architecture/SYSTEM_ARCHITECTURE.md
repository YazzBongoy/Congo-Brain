# Architecture Système — GEOS (Government Economic Optimization System)

## Vue d'ensemble
GEOS est une plateforme de gouvernance IA basée sur une architecture modulaire combinant optimisation mathématique, intelligence artificielle et simulation numérique.

## Architecture
```
┌─────────────────────────────────────────────────┐
│                 Frontend React                   │
│  Dashboard │ Provinces │ Ministères │ Ressources │
│  Entreprises │ Projets │ Services │ Prédiction   │
├─────────────────────────────────────────────────┤
│                  nginx proxy                     │
│              /api → backend:8000                  │
├─────────────────────────────────────────────────┤
│              FastAPI Backend                      │
│  Auth │ GEOS API │ IA GOV │ Monitoring │ GraphQL │
├─────────────────────────────────────────────────┤
│           8 Modules IA GOV                       │
│  Resource │ CS │ PS │ NRV │ Governance           │
│  Corruption │ Digital Twin │ Decision AI         │
├─────────────────────────────────────────────────┤
│         SNNOptimizationEngine                    │
│  14 entités │ Formule SNN │ Optimisation LP      │
├─────────────────────────────────────────────────┤
│    PostgreSQL │ Keycloak │ Prometheus │ Grafana   │
└─────────────────────────────────────────────────┘
```

## Composants
| Composant | Technologie | Rôle |
|-----------|------------|------|
| Frontend | React 18 + TypeScript + Vite | Interface utilisateur |
| API | FastAPI + Python 3.11+ | Backend REST |
| Auth | Keycloak 24 + JWT RS256 | Identification & RBAC |
| Base | PostgreSQL 16 | Stockage persistant |
| IA | 8 modules natifs Python | Optimisation & prédiction |
| Monitoring | Prometheus + Grafana | Métriques & alertes |
| CI/CD | GitHub Actions + GHCR | Déploiement automatisé |
| Conteneurs | Docker Compose | Orchestration locale |

## Flux de Données
1. Collecteurs → Base PostgreSQL (14 tables)
2. SNNOptimizationEngine → calcul SNN en temps réel
3. 8 modules IA → analyses par domaine
4. Predictor → projections 5-10 ans (Monte Carlo)
5. API REST → Frontend React + clients externes
6. Prometheus → Grafana dashboards

## Sécurité
- JWT RS256 avec JWKS Keycloak
- 3 rôles RBAC: admin, analyst, viewer
- Rate limiting (slowapi)
- HTTPS en production
- Secrets via variables d'environnement
