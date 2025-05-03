FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# Создание директории для логов
RUN mkdir -p /var/log/django && chmod 777 /var/log/django

# Копирование кода приложения
COPY . /app/

# Создание пользователя для запуска приложения
RUN useradd -m appuser && chown -R appuser:appuser /app /var/log/django
USER appuser

# Запуск приложения
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"] 