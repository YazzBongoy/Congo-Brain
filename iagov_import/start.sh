#!/usr/bin/env bash
set -e

echo "=== Congo-Brain: Initializing database ==="
congo-brain db init

echo "=== Congo-Brain: Seeding data ==="
congo-brain db seed

echo "=== Congo-Brain: Starting server on port 10000 ==="
exec uvicorn congo_brain.api.server:app --host 0.0.0.0 --port 10000
