"""Application configuration via environment variables."""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database URL — supports both SQLite (development) and PostgreSQL (production)
DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'congo_brain.db'}")
IS_POSTGRES: bool = DATABASE_URL.startswith("postgresql")

# Security
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
if SECRET_KEY == "change-me-in-production" and ENVIRONMENT != "development":
    print(
        "FATAL: SECRET_KEY must be set to a secure value in production. Set the SECRET_KEY environment variable.",
        file=sys.stderr,
    )
    sys.exit(1)

JWT_ALGORITHM: str = "HS256"
JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
PUBLIC_REGISTRATION_ENABLED: bool = os.getenv(
    "PUBLIC_REGISTRATION_ENABLED",
    "true" if ENVIRONMENT == "development" else "false",
).lower() == "true"

# Keycloak integration
KEYCLOAK_ENABLED: bool = os.getenv("KEYCLOAK_ENABLED", "false").lower() == "true"
if ENVIRONMENT in {"production", "staging"} and not KEYCLOAK_ENABLED:
    print(
        "FATAL: KEYCLOAK_ENABLED must be true in production and staging.",
        file=sys.stderr,
    )
    sys.exit(1)
KEYCLOAK_SERVER_URL: str = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080")
KEYCLOAK_REALM: str = os.getenv("KEYCLOAK_REALM", "congo-brain")
KEYCLOAK_CLIENT_ID: str = os.getenv("KEYCLOAK_CLIENT_ID", "congo-brain-api")
KEYCLOAK_CLIENT_SECRET: str = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
KEYCLOAK_JWKS_URL: str = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
KEYCLOAK_TOKEN_URL: str = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
KEYCLOAK_ISSUER: str = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}"

# AI thresholds
ANOMALY_THRESHOLD: float = float(os.getenv("ANOMALY_THRESHOLD", "0.7"))
RISK_SCORE_THRESHOLD: float = float(os.getenv("RISK_SCORE_THRESHOLD", "75.0"))

# Rate limiting
RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
