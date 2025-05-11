#!/bin/sh
set -e

# Запускаем MinIO в фоне
minio server /data --console-address ":9001" &

# Ждём пока MinIO запустится
echo "Waiting for MinIO to start..."
until curl -s http://localhost:9000/minio/health/live > /dev/null; do
  sleep 1
done

# Настраиваем mc client
mc alias set local http://localhost:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

# Создаём buckets
mc mb local/templates-assets --ignore-existing
mc mb local/generated-documents --ignore-existing

# Устанавливаем политики
mc policy set public local/templates-assets
mc policy set none local/generated-documents

echo "MinIO buckets and policies configured successfully"

# Возвращаем управление основному процессу
wait 