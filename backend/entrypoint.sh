#!/bin/bash
set -e

# Ждем базу данных
echo "Waiting for database..."
while ! python -c "import psycopg2; psycopg2.connect(dbname='${DB_NAME}', user='${DB_USER}', password='${DB_PASSWORD}', host='${DB_HOST}', port='${DB_PORT}')" 2>/dev/null; do
  echo "Database not available, waiting..."
  sleep 1
done
echo "Database ready!"

# Ждем MinIO
echo "Waiting for MinIO..."
while ! nc -z minio 9000; do
  sleep 1
done
echo "MinIO ready!"

# Определяем первый аргумент команды
COMMAND=$1

# Выполняем миграции только для основного контейнера, не для celery
if [[ $COMMAND != *"celery"* ]]; then
  echo "Applying database migrations..."
  python manage.py migrate

  # Собираем статические файлы
  echo "Collecting static files..."
  python manage.py collectstatic --noinput

  # Создаем суперпользователя, если его нет
  echo "Creating superuser..."
  cat > /tmp/create_superuser.py << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin@example.com', 'admin', username='admin')
    print('Superuser created.')
else:
    print('Superuser already exists.')
EOF
  python manage.py shell < /tmp/create_superuser.py
  rm /tmp/create_superuser.py

  # Запускаем начальную настройку, если файл существует
  if [ -f "setup/setup.py" ]; then
      echo "Running initial setup..."
      cd /app && python -m setup.setup
  fi
fi

# Для celery контейнеров просто ждем, пока будут выполнены миграции
if [[ $COMMAND == *"celery"* ]]; then
  echo "Waiting for migrations to complete..."
  # Ждем 10 секунд для выполнения миграций
  sleep 10
fi

# Запускаем command
exec "$@" 