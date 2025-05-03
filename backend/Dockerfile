# Мультистейд сборка для уменьшения размера финального образа
FROM python:3.11-slim as builder

WORKDIR /app

# Устанавливаем зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements
COPY requirements/ /app/requirements/

# Устанавливаем зависимости
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements/prod.txt

# Финальный образ
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем runtime зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Копируем wheels из builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements /app/requirements

# Устанавливаем зависимости из wheels
RUN pip install --no-cache /wheels/*

# Копируем код приложения
COPY . /app/

# Создание пользователя для запуска приложения
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Создаем директории для логов и staticfiles
RUN mkdir -p /var/log/django /app/staticfiles /app/mediafiles && \
    chown -R appuser:appuser /var/log/django /app/staticfiles /app/mediafiles

# Entrypoint скрипт
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser

# Собираем статические файлы
RUN python manage.py collectstatic --noinput || true

# Expose порт
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"] 