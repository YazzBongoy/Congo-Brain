# Déploiement — GEOS

## Docker Compose (6 services durables + 2 jobs one-shot)
```yaml
services:
  postgres:     PostgreSQL 16       → port 5432
  keycloak:     Keycloak 24         → port 8080
  migrate:      Alembic             → termine avant l'API
  keycloak-init:réconciliation SSO   → termine avant l'API
  app:          FastAPI + Uvicorn   → port 8000
  frontend:     React + nginx       → port 3000
  prometheus:   Prometheus v2.53    → port 9090
  grafana:      Grafana 11.1        → port 3001
```

### Démarrage
```bash
docker compose up -d --build
```

### Variables d'environnement
```env
POSTGRES_PASSWORD=<injecté depuis un gestionnaire de secrets>
DATABASE_URL=postgresql+psycopg2://congo:<mot-de-passe>@postgres:5432/congo_brain
SECRET_KEY=<au moins 32 octets aléatoires>
KEYCLOAK_ADMIN_PASSWORD=<secret local Compose>
KEYCLOAK_CLIENT_SECRET=<secret client aléatoire>
GRAFANA_ADMIN_PASSWORD=<secret local Compose>
KEYCLOAK_SERVER_URL=http://keycloak:8080
KEYCLOAK_REALM=congo-brain
KEYCLOAK_CLIENT_ID=congo-brain-api
KEYCLOAK_ENABLED=true
ENVIRONMENT=development
```

`docker compose up` exécute obligatoirement `alembic upgrade head` et la réconciliation Keycloak avant de démarrer
l'API. Si l'ancien compte de démonstration `admin/admin123` est détecté, le job Keycloak échoue jusqu'à approbation
explicite avec `CONFIRM_REMOVE_LEGACY_ADMIN=REMOVE`.

## CI/CD (GitHub Actions)
Pipeline `.github/workflows/ci.yml`:
1. **Backend** — Ruff, compile/import smoke, Mypy, pytest, migrations PostgreSQL et audit d'intégrité
2. **Frontend** — installation propre, build TypeScript/Vite et audit npm
3. **Conteneurs** — builds API et frontend sur chaque PR
4. **Publication GHCR** — uniquement avec un tag `sha-<commit>` immuable après succès sur `main`

### Déclencheurs
- Push sur `main`
- Pull request sur `main`

## Production
La production utilise Render ou Helm avec Keycloak activé. Les secrets sont injectés par la plateforme ; ils ne sont
jamais stockés dans les values Helm ni dans Docker Compose. Le pre-deploy Render enchaîne Alembic puis la réconciliation
Keycloak. Helm exécute d'abord le hook `keycloak-init` (poids `-10`), puis le hook Alembic (poids `-5`) ; un échec de
l'un des deux bloque le rollout. Exécuter `scripts/release_checklist.sh` contre le staging avant toute promotion.

Le runbook de sauvegarde et de restauration PostgreSQL est disponible dans
[`POSTGRES_BACKUP_RESTORE.md`](POSTGRES_BACKUP_RESTORE.md).

## Kubernetes (Phase 5)
- Helm chart applicatif consommant une base PostgreSQL managée externe
- ConfigMaps pour configuration
- Secrets externes précréés obligatoires pour `DATABASE_URL`, `SECRET_KEY`, le mot de passe administrateur Keycloak et
  le secret client. Le Secret d'identité peut aussi porter `confirm-remove-legacy-admin=REMOVE` après approbation.
- Ingress pour routing
- HPA pour autoscaling
- Jobs Helm de réconciliation Keycloak et Alembic `pre-install` / `pre-upgrade`, avant les workloads

Le chart ne provisionne pas PostgreSQL, Prometheus ou Grafana. Ces services relèvent de la plateforme d'exploitation
et doivent disposer de leurs propres politiques de sauvegarde, haute disponibilité et supervision.
