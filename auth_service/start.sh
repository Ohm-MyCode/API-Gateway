#!/bin/sh
set -e

/app/.venv/bin/alembic -c /app/auth_service/alembic.ini upgrade head

exec /app/.venv/bin/uvicorn auth_service.main:app \
    --host 0.0.0.0 \
    --port 8000