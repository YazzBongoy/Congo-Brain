"""Application configuration via environment variables."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'congo_brain.db'}")

SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

ANOMALY_THRESHOLD: float = float(os.getenv("ANOMALY_THRESHOLD", "0.7"))
RISK_SCORE_THRESHOLD: float = float(os.getenv("RISK_SCORE_THRESHOLD", "75.0"))
