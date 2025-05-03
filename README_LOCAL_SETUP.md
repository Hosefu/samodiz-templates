# Локальная настройка для разработки

## Быстрый старт с SQLite (рекомендуется для разработки)

### 1. Подготовка окружения

```bash
# Создание виртуального окружения
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установка зависимостей для разработки
pip install -r requirements/local.txt
```

### 2. Настройка переменных окружения

```bash
# Создание .env файла
cp .env.example .env

# Опционально: отредактируйте .env для своих настроек
DJANGO_ENV=local
DEBUG=True
```

### 3. Инициализация базы данных

```bash
# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Запуск начальной настройки (создание форматов, единиц измерения)
python setup.py
```

### 4. Запуск сервера разработки

```bash
# Запуск Django сервера
python manage.py runserver

# В отдельном терминале: запуск Celery worker (если нужно)
celery -A core worker -l INFO

# В отдельном терминале: запуск Celery beat (если нужно)
celery -A core beat -l INFO
```

## Запуск с Docker для разработки

### 1. Использование SQLite внутри контейнера

```bash
# Запуск с SQLite
docker-compose -f docker-compose.dev.yml up --build
```

### 2. Полный запуск с PostgreSQL

```bash
# Запуск со всеми сервисами включая PostgreSQL
docker-compose up --build
```

## Тестирование

### Запуск тестов локально

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=apps --cov-report=html

# Быстрые тесты (без Celery)
pytest -m "not celery"
```

### Запуск тестов в Docker

```bash
# Тесты в контейнере
docker-compose run backend pytest

# Тесты с покрытием
docker-compose run backend pytest --cov=apps --cov-report=html
```

## Очистка и сброс

### Очистка локально

```bash
# Удаление базы данных SQLite
rm db.sqlite3

# Удаление всех миграций (сохраняя __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Повторная инициализация
python manage.py makemigrations
python manage.py migrate
python setup.py
```

### Очистка Docker

```bash
# Удаление контейнеров и томов
docker-compose down -v

# Пересборка образов
docker-compose build --no-cache
```

## Отладка

### Django Shell

```bash
# Локально
python manage.py shell

# В Docker
docker-compose run backend python manage.py shell
```

### Django Admin

Доступ к админке:
- URL: http://localhost:8000/admin/
- Логин: admin
- Пароль: admin (по умолчанию)

### API Documentation

- Swagger UI: http://localhost:8000/docs/
- ReDoc: http://localhost:8000/redoc/
- OpenAPI схема: http://localhost:8000/openapi.json 