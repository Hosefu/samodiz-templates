FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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