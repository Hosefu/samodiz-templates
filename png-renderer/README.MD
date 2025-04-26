## Обзор

PNG Renderer - это сервис на Python с использованием FastAPI, который генерирует PNG-изображения из HTML-шаблонов. Сервис использует Playwright для рендеринга HTML в PNG и предоставляет REST API для взаимодействия с другими компонентами системы.

## Архитектура

```
png-renderer/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Основной файл FastAPI приложения
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py            # API маршруты
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cache.py             # Сервис кэширования
│   │   └── renderer.py          # Сервис рендеринга PNG
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py           # Модели запросов
│   │   └── response.py          # Модели ответов
│   ├── utils/
│   │   ├── __init__.py
│   │   └── unit_converter.py    # Утилиты для конвертации единиц измерения
│   └── config.py                # Конфигурация приложения
├── logs/                        # Директория для логов
├── output/                      # Директория для выходных файлов
├── temp/                        # Директория для временных файлов
├── Dockerfile                   # Инструкции для сборки Docker-образа
└── requirements.txt             # Зависимости Python
```

## Компоненты

### Main (app/main.py)

Точка входа FastAPI-приложения. Инициализирует приложение, настраивает middleware, маршруты и обработчики событий.

**Ключевые функции**:

- Инициализация FastAPI-приложения
- Настройка CORS
- Регистрация маршрутов API
- Обработка исключений
- Создание необходимых директорий

### API Routes (app/api/routes.py)

Определяет маршруты API для обработки запросов.

**Ключевые функции**:

- `render_png`: Обработка запросов на рендеринг PNG
- `health_check`: Проверка работоспособности сервиса

### Renderer (app/services/renderer.py)

Реализует логику рендеринга HTML в PNG с использованием Playwright.

**Ключевые функции**:

- `render_png`: Рендеринг HTML в PNG
- `_render_with_playwright`: Рендеринг с использованием Playwright
- `_calculate_dimensions`: Расчет размеров в пикселях

### Cache (app/services/cache.py)

Реализует кэширование результатов рендеринга для повышения производительности.

**Ключевые функции**:

- `get_cache_key`: Генерация ключа кэша
- `get_from_cache`: Получение результата из кэша
- `save_to_cache`: Сохранение результата в кэш

### Models (app/models)

Определяет модели данных для запросов и ответов.

**Ключевые модели**:

- `RenderRequest`: Запрос на рендеринг PNG
- `RenderResponse`: Ответ на запрос рендеринга
- `HealthResponse`: Ответ на запрос проверки работоспособности

### Unit Converter (app/utils/unit_converter.py)

Предоставляет функции для конвертации единиц измерения.

**Ключевые функции**:

- `mm_to_pixels`: Конвертация миллиметров в пиксели
- `pixels_to_mm`: Конвертация пикселей в миллиметры
- `points_to_pixels`: Конвертация пунктов в пиксели
- `calculate_dimensions`: Расчет размеров на основе единиц измерения

### Config (app/config.py)

Определяет конфигурацию приложения с использованием pydantic и переменных окружения.

**Ключевые настройки**:

- `APP_NAME`: Название приложения
- `DEBUG`: Режим отладки
- `HOST`, `PORT`: Настройки HTTP-сервера
- `CACHE_DIR`, `CACHE_ENABLED`, `CACHE_EXPIRATION`: Настройки кэширования
- `DEFAULT_DPI`, `DEFAULT_FORMAT`, `DEFAULT_QUALITY`: Настройки рендеринга
- `TEMP_DIR`, `OUTPUT_DIR`: Пути к директориям
- `LOG_LEVEL`: Уровень логирования
- `BROWSER_TYPE`, `BROWSER_HEADLESS`, `BROWSER_ARGS`: Настройки Playwright
- `MAX_CONCURRENT_BROWSERS`: Максимальное количество параллельных браузеров
- `RENDER_TIMEOUT`: Таймаут рендеринга

## Рабочий процесс

1. Клиент отправляет запрос на генерацию PNG на `/api/png/render`
2. `render_png` в `routes.py` проверяет запрос и извлекает параметры
3. Проверяется наличие результата в кэше
4. Если результат не найден в кэше:
    - Рассчитываются размеры в пикселях
    - Создается Playwright-браузер
    - HTML рендерится в PNG
    - Результат сохраняется в кэш
5. Возвращается PNG-изображение с соответствующими заголовками

## API-интерфейсы

### Рендеринг PNG

**Запрос**:

```
POST /api/png/render
Content-Type: application/json

{
  "html": "<html><body><h1>Заголовок</h1><p>Содержание</p></body></html>",
  "width": 800,
  "height": 600,
  "units": "px",
  "settings": {
    "dpi": 96,
    "transparency": "true"
  }
}
```

**Ответ**: PNG-изображение с соответствующим Content-Type или информация об ошибке в формате JSON.

### Проверка работоспособности

**Запрос**:

```
GET /api/png/health
```

**Ответ**:

json

```json
{
  "status": "ok",
  "service": "png-renderer"
}
```

## Настройка и запуск

### Переменные окружения

- `PNG_RENDERER_HOST`: Хост для HTTP-сервера (по умолчанию "0.0.0.0")
- `PNG_RENDERER_PORT`: Порт для HTTP-сервера (по умолчанию 8082)
- `PNG_RENDERER_LOG_LEVEL`: Уровень логирования (по умолчанию "INFO")
- `PNG_RENDERER_CACHE_ENABLED`: Включение кэширования (по умолчанию "True")
- `PNG_RENDERER_BROWSER_TYPE`: Тип браузера (по умолчанию "chromium")
- `PNG_RENDERER_BROWSER_HEADLESS`: Режим headless (по умолчанию "True")
- `PNG_RENDERER_MAX_CONCURRENT_BROWSERS`: Максимальное количество параллельных браузеров (по умолчанию 5)

### Запуск через Docker

bash

```bash
docker build -t png-renderer .
docker run -p 8082:8082 \
  -e PNG_RENDERER_HOST=0.0.0.0 \
  -e PNG_RENDERER_PORT=8082 \
  -e PNG_RENDERER_LOG_LEVEL=INFO \
  -e PNG_RENDERER_CACHE_ENABLED=True \
  png-renderer
```

### Запуск локально

bash

```bash
# Установка зависимостей
pip install -r requirements.txt

# Установка браузеров для Playwright
playwright install chromium

# Запуск сервиса
uvicorn app.main:app --host 0.0.0.0 --port 8082
```

## Расширение функциональности

### Добавление новых форматов изображений

1. Расширить `renderer.py` для поддержки новых форматов (JPEG, WebP)
2. Обновить `routes.py` для обработки запросов с новыми форматами
3. Адаптировать `cache.py` для кэширования новых форматов

### Улучшение производительности

1. Оптимизировать кэширование в `cache.py`
2. Реализовать пулинг браузеров в `renderer.py`
3. Добавить возможность параллельной обработки нескольких запросов