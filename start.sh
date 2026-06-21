#!/bin/sh

set -e

echo "Running database migrations..."

until alembic upgrade head; do
  echo "Database is not ready yet. Retrying in 2 seconds..."
  sleep 2
done

echo "Starting FastAPI app..."

exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}