FROM python:3.10-slim

# Установка зависимостей для Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка браузеров для Playwright
RUN playwright install chromium

# Создание директорий для работы приложения
RUN mkdir -p /app/output /app/logs /tmp/png-renderer/cache /tmp/png-renderer/temp
RUN chmod -R 777 /app/output /app/logs /tmp/png-renderer

# Копирование кода приложения
COPY ./app /app/app

# Переменные окружения по умолчанию
ENV PNG_RENDERER_HOST="0.0.0.0"
ENV PNG_RENDERER_PORT="8082"
ENV PNG_RENDERER_LOG_LEVEL="INFO"
ENV PNG_RENDERER_DEBUG="False"
ENV PNG_RENDERER_BROWSER_TYPE="chromium"
ENV PNG_RENDERER_BROWSER_HEADLESS="True"

# Экспорт порта
EXPOSE 8082

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8082"]