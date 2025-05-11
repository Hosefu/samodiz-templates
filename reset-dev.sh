#!/bin/bash
# Быстрый сброс для разработки

echo "Stopping containers..."
docker-compose down

echo "Removing volumes (except Postgres)..."
docker volume rm samodes_redis_data samodes_storage_data samodes_static_data samodes_media_data 2>/dev/null || true

echo "Starting fresh containers..."
docker-compose up -d

echo "Waiting for services to start..."
sleep 10

echo "Running migrations and setup..."
docker exec backend python manage.py migrate
docker exec backend python manage.py collectstatic --noinput
docker exec backend python -m setup.setup

echo "Development environment reset complete!" 