FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем зависимости
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . /app/

# Создаем пользователя
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Создаем необходимые директории
RUN mkdir -p /var/log/django /app/staticfiles /app/mediafiles /app/storage && \
    chown -R appuser:appuser /var/log/django /app/staticfiles /app/mediafiles /app/storage

# Entrypoint скрипт
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"] 