#!/bin/sh
echo "Waiting for PostgreSQL to start..."
sleep 5
echo "Running migrations..."
alembic upgrade head
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 