# Déploiement — GEOS

## Docker Compose (6 services)
```yaml
services:
  postgres:     PostgreSQL 16       → port 5432
  keycloak:     Keycloak 24         → port 8080
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
DATABASE_URL=postgresql+psycopg2://congo:congo_secret_2026@postgres:5432/congo_brain
SECRET_KEY=super-secret-key-change-in-production
KEYCLOAK_SERVER_URL=http://keycloak:8080
KEYCLOAK_REALM=congo-brain
KEYCLOAK_CLIENT_ID=congo-brain-api
KEYCLOAK_ENABLED=true
ENVIRONMENT=development
```

## CI/CD (GitHub Actions)
Pipeline `.github/workflows/ci.yml`:
1. **Test** — pytest sur Python 3.11/3.12/3.13
2. **Build Docker** — multi-platform (amd64/arm64)
3. **Push GHCR** — image `ghcr.io/yazzbongoy/congo-brain`
4. **Tag auto** — version basée sur date

### Déclencheurs
- Push sur `main`
- Pull request sur `main`

## Production
```bash
# Variables sécurisées
export DATABASE_URL="postgresql://..."
export SECRET_KEY="$(openssl rand -hex 32)"
export KEYCLOAK_ENABLED="false"

# Lancer
docker compose -f docker-compose.yml up -d
```

## Kubernetes (Phase 5)
- Helm charts pour déploiement K8s
- ConfigMaps pour configuration
- Secrets pour credentials
- Ingress pour routing
- HPA pour autoscaling
