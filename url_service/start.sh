#!/bin/sh
set -e

/app/.venv/bin/alembic -c /app/url_service/alembic.ini upgrade head

exec /app/.venv/bin/uvicorn url_service.main:app \
    --host 0.0.0.0 \
    --port 8000