## Обзор

Template Service - это сервис на Python с использованием FastAPI, предназначенный для обработки HTML-шаблонов с поддержкой условных конструкций и других продвинутых возможностей шаблонизации. Сервис использует Jinja2 для обработки шаблонов и предоставляет REST API для взаимодействия с другими компонентами системы.

## Архитектура

```
template-service/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Основной файл FastAPI приложения
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py            # API маршруты
│   ├── services/
│   │   ├── __init__.py
│   │   └── template_engine.py   # Сервис обработки шаблонов (Jinja2)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py           # Модели запросов
│   │   └── response.py          # Модели ответов
│   └── utils/
│       ├── __init__.py
│       └── logger.py            # Настройка логирования
├── logs/                        # Директория для логов
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
- Логирование запросов и ответов

### API Routes (app/api/routes.py)

Определяет маршруты API для обработки запросов.

**Ключевые функции**:

- `render_template`: Обработка запросов на рендеринг шаблона
- `health_check`: Проверка работоспособности сервиса

### Template Engine (app/services/template_engine.py)

Реализует логику обработки шаблонов с использованием Jinja2.

**Ключевые функции**:

- `render_template`: Обработка HTML-шаблона с подстановкой данных
- `_render_with_jinja`: Рендеринг шаблона с использованием Jinja2
- `_render_simple_template`: Простая замена плейсхолдеров для обратной совместимости
- `_check_for_unrendered_placeholders`: Проверка наличия неподставленных плейсхолдеров

### Models (app/models)

Определяет модели данных для запросов и ответов.

**Ключевые модели**:

- `TemplateRenderRequest`: Запрос на обработку шаблона
- `TemplateRenderResponse`: Ответ на запрос обработки шаблона
- `HealthResponse`: Ответ на запрос проверки работоспособности

### Logger (app/utils/logger.py)

Настраивает логирование с помощью библиотеки loguru.

**Ключевые функции**:

- `setup_logging`: Настройка логирования с указанием уровня и форматирования

## Синтаксис шаблонов

Template Service поддерживает два формата шаблонов:

### 1. Простые плейсхолдеры (обратная совместимость)

html

```html
<p>Имя: {{name}}</p>
<p>Дата: {{date}}</p>
```

### 2. Расширенный синтаксис Jinja2

html

```html
<p>Имя: {{ name }}</p>
<p>Дата: {{ date }}</p>

{% if show_details %}
  <div class="details">
    <h2>Подробная информация</h2>
    <p>{{ details }}</p>
  </div>
{% endif %}

{% for item in items %}
  <li>{{ item.name }}: {{ item.value }}</li>
{% endfor %}
```

## API-интерфейсы

### Обработка шаблона

**Запрос**:

```
POST /api/template/render
Content-Type: application/json

{
  "template_html": "<div>{% if show_details %}<p>{{ details }}</p>{% endif %}</div>",
  "data": {
    "show_details": true,
    "details": "Подробная информация"
  },
  "template_id": 1,
  "page_index": 0
}
```

**Ответ**:

json

```json
{
  "html": "<div><p>Подробная информация</p></div>",
  "status": "success"
}
```

### Проверка работоспособности

**Запрос**:

```
GET /api/template/health
```

**Ответ**:

json

```json
{
  "status": "ok",
  "service": "template-service"
}
```

## Обработка ошибок

### Ошибки синтаксиса шаблона

Если шаблон содержит синтаксические ошибки, сервис возвращает ответ с кодом 400 и подробным описанием ошибки:

json

```json
{
  "detail": "Template syntax error at line 3: unexpected '}'.\nContext:\n<div>{% if show_details %}<p>{{ details }}</p>{% endif }}</div>"
}
```

### Другие ошибки

- Пустой шаблон: код 400, `"detail": "Template HTML is required"`
- Внутренние ошибки: код 500, `"detail": "Internal server error: [описание ошибки]"`

## Настройка и запуск

### Переменные окружения

- `TEMPLATE_SERVICE_HOST`: Хост для HTTP-сервера (по умолчанию "0.0.0.0")
- `TEMPLATE_SERVICE_PORT`: Порт для HTTP-сервера (по умолчанию 8083)
- `TEMPLATE_SERVICE_LOG_LEVEL`: Уровень логирования (по умолчанию "INFO")
- `TEMPLATE_SERVICE_DEBUG`: Режим отладки (по умолчанию "False")

### Запуск через Docker

bash

```bash
docker build -t template-service .
docker run -p 8083:8083 \
  -e TEMPLATE_SERVICE_HOST=0.0.0.0 \
  -e TEMPLATE_SERVICE_PORT=8083 \
  -e TEMPLATE_SERVICE_LOG_LEVEL=INFO \
  template-service
```

### Запуск локально

bash

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервиса
uvicorn app.main:app --host 0.0.0.0 --port 8083
```

## Расширение функциональности

### Добавление новых возможностей шаблонизации

Благодаря использованию Jinja2, сервис можно легко расширить, добавив поддержку:

1. **Циклов**:

html

```html
{% for item in items %}
  <li>{{ item.name }}: {{ item.value }}</li>
{% endfor %}
```

2. **Фильтров**:

html

```html
{{ text | upper }}
{{ date | date("Y-m-d") }}
```

3. **Макросов**:

html

```html
{% macro input(name, value='', type='text') %}
  <input type="{{ type }}" name="{{ name }}" value="{{ value }}">
{% endmacro %}

{{ input('username') }}
{{ input('password', type='password') }}
```

### Добавление пользовательских фильтров

Можно добавить пользовательские фильтры в `template_engine.py`:

python

```python
def custom_filter(value):
    # Реализация фильтра
    return processed_value

# В конструкторе TemplateEngine:
self.env.filters['custom_filter'] = custom_filter
```

### Добавление кэширования шаблонов

Для повышения производительности можно добавить кэширование обработанных шаблонов:

python

```python
from functools import lru_cache

class TemplateEngine:
    # ...
    
    @lru_cache(maxsize=100)
    def _get_template(self, template_html):
        return self.env.from_string(template_html)
```