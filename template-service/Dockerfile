FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей и инструментов для health check
COPY requirements.txt .
RUN apt-get update && apt-get install -y wget && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Создание директорий для логов
RUN mkdir -p /app/logs

# Копирование кода приложения
COPY . .

# Переменные окружения
ENV TEMPLATE_SERVICE_HOST="0.0.0.0"
ENV TEMPLATE_SERVICE_PORT="8083"
ENV TEMPLATE_SERVICE_LOG_LEVEL="INFO"

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8083"]