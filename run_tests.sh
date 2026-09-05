#!/usr/bin/env bash

set -e

echo "Activating virtual environment..."
source .venv/bin/activate

if [ ! -f app/secrets/private.pem ]; then
    echo "Generating RSA keypair..."

    mkdir -p app/secrets

    openssl genrsa -out app/secrets/private.pem 4096

    openssl rsa \
      -in app/secrets/private.pem \
      -pubout \
      -out app/secrets/public.pem
fi

echo "Starting URL service test database..."
docker run --rm -d \
  --name test-postgres2 \
  -e POSTGRES_USER=test \
  -e POSTGRES_PASSWORD=test \
  -e POSTGRES_DB=urltestdb \
  -p 5434:5432 \
  postgres:17

echo "Waiting for URL DB..."
until docker exec test-postgres2 pg_isready -U test >/dev/null 2>&1; do
  sleep 1
done

echo "Running URL migrations..."
URL_DB="postgresql+psycopg://test:test@localhost:5434/urltestdb" \
alembic -c url_service/alembic.ini upgrade head

echo "Starting Auth service test database..."
docker run --rm -d \
  --name test-postgres \
  -e POSTGRES_USER=test \
  -e POSTGRES_PASSWORD=test \
  -e POSTGRES_DB=authtestdb \
  -p 5433:5432 \
  postgres:17

echo "Waiting for Auth DB..."
until docker exec test-postgres pg_isready -U test >/dev/null 2>&1; do
  sleep 1
done

echo "Running Auth migrations..."
AUTH_DB="postgresql+psycopg://test:test@localhost:5433/authtestdb" \
alembic -c auth_service/alembic.ini upgrade head

echo "Starting Redis..."
docker run --rm -d \
  --name test1-redis \
  -p 6379:6379 \
  redis:latest

echo "Waiting for Redis..."
until docker exec test1-redis redis-cli ping >/dev/null 2>&1; do
  sleep 1
done

echo "Running Auth Service tests..."
pytest tests/auth_service_test

echo "Running Gateway tests..."
pytest tests/gateway

echo "Running URL Service tests..."
pytest tests/url_service

echo "All tests completed successfully."