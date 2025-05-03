#!/bin/bash
set -e

# Ждем базу данных
echo "Waiting for database..."
while ! python -c "import psycopg2; psycopg2.connect(dbname='${DB_NAME}', user='${DB_USER}', password='${DB_PASSWORD}', host='${DB_HOST}', port='${DB_PORT}')" 2>/dev/null; do
  echo "Database not available, waiting..."
  sleep 1
done
echo "Database ready!"

# Выполняем миграции
echo "Applying database migrations..."
python manage.py migrate

# Собираем статические файлы
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Создаем суперпользователя, если его нет
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created.')
else:
    print('Superuser already exists.')
"

# Запускаем начальную настройку, если файл существует
if [ -f "setup.py" ]; then
    echo "Running initial setup..."
    python setup.py
fi

# Запускаем command
exec "$@" 