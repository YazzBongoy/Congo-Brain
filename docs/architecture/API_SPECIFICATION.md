# Spécification API — GEOS

## Base URL
```
http://localhost:8000/api/v1
```

## Auth
```
POST /auth/register    → inscription
POST /auth/login       → token JWT
GET  /auth/me          → profil
GET  /auth/users       → liste (admin)
PUT  /auth/users/{id}  → modifier rôle (admin)
DELETE /auth/users/{id} → supprimer (admin)
GET  /auth/roles       → lister rôles
```

## GEOS (22 endpoints)
```
GET  /geos/dashboard           → dashboard complet SNN
GET  /geos/snn                 → détail SNN agrégé
POST /geos/optimize            → optimisation LP

GET  /geos/provinces           → liste 8 provinces
GET  /geos/provinces/{name}    → détails province

GET  /geos/companies           → liste 8 entreprises
GET  /geos/companies/ps/total  → PS total par entreprise

GET  /geos/ministries          → liste 8 ministères
GET  /geos/ministries/ranking  → classement par score

GET  /geos/resources           → liste 8 ressources
GET  /geos/resources/nrv/total → NRV total
GET  /geos/resources/ec/total  → EC total

GET  /geos/taxes               → liste 6 impôts
GET  /geos/taxes/revenue-total → recettes totales

GET  /geos/projects            → liste 8 projets
GET  /geos/projects/snn/total  → SNN total projets

GET  /geos/public-services     → liste 8 services
GET  /geos/public-services/cs/total → CS total

GET  /geos/contracts           → liste 6 contrats
GET  /geos/payments            → liste paiements
GET  /geos/markets             → liste 5 marchés
GET  /geos/indicators          → liste 8 indicateurs

GET  /geos/predictions/scenarios     → 7 scénarios
GET  /geos/predictions/compare       → comparaison + ranking
GET  /geos/predictions/{key}         → prédiction détaillée
```

## IA GOV (15 endpoints)
```
GET  /ia-gov/resource/dashboard
POST /ia-gov/resource/optimize
POST /ia-gov/resource/simulate

GET  /ia-gov/consumer/dashboard
POST /ia-gov/consumer/simulate

GET  /ia-gov/producer/dashboard
POST /ia-gov/producer/simulate

GET  /ia-gov/national/dashboard
POST /ia-gov/national/compare

GET  /ia-gov/governance/dashboard
POST /ia-gov/governance/improve

GET  /ia-gov/corruption/dashboard
GET  /ia-gov/corruption/by-sector

GET  /ia-gov/digital-twin/dashboard
POST /ia-gov/digital-twin/invest

GET  /ia-gov/decision/ask
```

## Monitoring
```
GET  /metrics              → Prometheus metrics
GET  /health/detailed      → santé détaillée
GET  /health               → health check
```

## Auth
JWT Bearer token requis pour les endpoints protégés.
Rôles: admin (tous), analyst (lecture+écriture), viewer (lecture seule).
