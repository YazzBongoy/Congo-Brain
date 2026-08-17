#!/usr/bin/env bash
set -e

echo "=== Congo-Brain: Running database migrations ==="
alembic upgrade head

echo "=== Congo-Brain: Seeding data (if empty) ==="
congo-brain db seed || echo "Seed skipped (data may already exist)"

echo "=== Congo-Brain: Starting server on port 10000 ==="
exec uvicorn congo_brain.api.server:app --host 0.0.0.0 --port 10000
