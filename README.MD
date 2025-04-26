# Система генерации документов - Подробная документация

## Обзор проекта

Система генерации документов представляет собой микросервисную архитектуру для создания документов различных форматов (PDF, PNG) из HTML-шаблонов с поддержкой динамических данных, условных конструкций и других продвинутых возможностей шаблонизации.

## Архитектура системы

Show Image

Система состоит из следующих компонентов:

1. **Frontend (React)** - пользовательский интерфейс для работы с системой
2. **Nginx** - обратный прокси-сервер и балансировщик нагрузки
3. **Storage Service (Django)** - хранение шаблонов и сгенерированных документов
4. **Render Routing Service (Go)** - маршрутизация запросов на рендеринг к соответствующим сервисам
5. **Template Service (Python/FastAPI)** - обработка шаблонов с поддержкой условных конструкций
6. **PDF Renderer (.NET)** - генерация PDF-документов из HTML
7. **PNG Renderer (Python/FastAPI)** - генерация PNG-изображений из HTML

### Схема взаимодействия компонентов

```
┌─────────────┐      ┌────────────────────┐      ┌─────────────┐
│             │      │                    │      │             │
│   Frontend  │─────▶│  Nginx Proxy/Load  │◀────▶│  Storage    │
│   (React)   │      │  Balancer          │      │  Service    │
│             │      │                    │      │  (Django)   │
└─────────────┘      └────────────────────┘      └─────────────┘
                               │                         ▲
                               │                         │
                               ▼                         │
                      ┌─────────────────┐               │
                      │                 │               │
                      │  Render Router  │───────────────┘
                      │  (Go)           │               ▲
                      │                 │               │
                      └─────────────────┘               │
                               │                        │
                               ▼                        │
                      ┌─────────────────┐               │
                      │                 │               │
                      │  Template       │───────────────┘
                      │  Service        │
                      │  (Python)       │
                      └─────────────────┘
                               │
                               ├─────────────┐
                               │             │
                               ▼             ▼
                      ┌─────────────┐ ┌─────────────┐
                      │             │ │             │
                      │PDF Renderer │ │PNG Renderer │
                      │(.NET)       │ │(Python)     │
                      │             │ │             │
                      └─────────────┘ └─────────────┘
```

## Рабочий процесс

1. **Создание шаблона**:
    - Пользователь создает HTML-шаблон с плейсхолдерами и условными конструкциями
    - Шаблон загружается в Storage Service
2. **Генерация документа**:
    - Пользователь выбирает шаблон и вводит данные через Frontend
    - Запрос отправляется через Nginx в Render Routing Service
    - Render Routing Service получает шаблон из Storage Service
    - Render Routing Service отправляет шаблон в Template Service для обработки
    - Template Service обрабатывает шаблон, подставляя данные и выполняя условные конструкции
    - Обработанный HTML отправляется в соответствующий рендерер (PDF или PNG)
    - Сгенерированный документ загружается обратно в Storage Service
    - URL документа возвращается пользователю

## Технический стек

- **Frontend**: React, TailwindCSS
- **Storage Service**: Django, Django REST Framework
- **Render Routing Service**: Go, Gin
- **Template Service**: Python, FastAPI, Jinja2
- **PDF Renderer**: .NET, iText7
- **PNG Renderer**: Python, FastAPI, Playwright
- **Инфраструктура**: Docker, Nginx

## Сервисы

### 1. Storage Service (Django)

**Назначение**: Хранение шаблонов и сгенерированных документов

**Ключевые особенности**:

- Управление метаданными шаблонов (имя, версия, тип)
- Хранение HTML-кода страниц шаблонов
- Управление полями для подстановки данных
- Хранение сгенерированных документов (PDF, PNG)
- REST API для доступа к шаблонам и документам

[Подробнее о Storage Service](./storage/README.md)

### 2. Render Routing Service (Go)

**Назначение**: Маршрутизация запросов на рендеринг к соответствующим сервисам

**Ключевые особенности**:

- Получение запросов на генерацию документов
- Извлечение шаблонов из Storage Service
- Взаимодействие с Template Service для обработки шаблонов
- Маршрутизация обработанных шаблонов к соответствующим рендерерам
- Загрузка сгенерированных документов в Storage Service

[Подробнее о Render Routing Service](./render-routing/README.md)

### 3. Template Service (Python/FastAPI)

**Назначение**: Обработка шаблонов с поддержкой условных конструкций

**Ключевые особенности**:

- Обработка HTML-шаблонов с использованием Jinja2
- Поддержка условных конструкций (`{% if условие %}...{% endif %}`)
- Подстановка данных в плейсхолдеры (`{{ переменная }}`)
- Обратная совместимость с простыми плейсхолдерами
- REST API для обработки шаблонов

[Подробнее о Template Service](./template-service/README.md)

### 4. PDF Renderer (.NET)

**Назначение**: Генерация PDF-документов из HTML

**Ключевые особенности**:

- Конвертация HTML в PDF с сохранением стилей
- Поддержка пользовательских шрифтов
- Настройка размеров страниц и полей
- Создание многостраничных документов (из нескольких HTML-блоков)
- Опциональная генерация превью документов

[Подробнее о PDF Renderer](./pdf-renderer/README.md)

### 5. PNG Renderer (Python/FastAPI)

**Назначение**: Генерация PNG-изображений из HTML

**Ключевые особенности**:

- Рендеринг HTML в PNG с помощью Playwright
- Настройка размеров изображений
- Поддержка различных единиц измерения (px, mm)
- Кэширование результатов рендеринга
- REST API для генерации изображений

[Подробнее о PNG Renderer](./png-renderer/README.md)

## Запуск проекта

### Предварительные требования

- Docker и Docker Compose
- Git

### Шаги по запуску

1. Клонировать репозиторий:

bash

```bash
git clone <repository_url>
cd document-generation-system
```

2. Создать файл `.env` с переменными окружения:

```
# Общие настройки
API_KEY=development-api-key

# Порты сервисов
FRONTEND_PORT=5173
STORAGE_PORT=8000
ROUTING_PORT=8080
PDF_PORT=8081
PNG_PORT=8082
TEMPLATE_PORT=8083

# Storage Service
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=your-secret-key-here

# Render Routing Service
LOGGER_LEVEL=info

# PDF Renderer
ASPNETCORE_ENVIRONMENT=Development

# PNG Renderer
PNG_RENDERER_LOG_LEVEL=INFO
PNG_RENDERER_CACHE_ENABLED=True

# Template Service
TEMPLATE_SERVICE_LOG_LEVEL=INFO
TEMPLATE_SERVICE_DEBUG=False
```

3. Запустить проект с помощью Docker Compose:

bash

```bash
docker-compose up --build
```

4. Открыть веб-интерфейс по адресу:

```
http://localhost
```

## API-интерфейсы

### Storage Service API

- `GET /api/templates/` - Получение списка шаблонов
- `GET /api/templates/{id}/` - Получение конкретного шаблона
- `POST /api/upload-template/` - Загрузка сгенерированного документа
- `GET /api/files/{id}/` - Получение сгенерированного документа

### Render Routing Service API

- `POST /api/render/generate` - Генерация документа из шаблона
- `GET /api/health` - Проверка работоспособности сервиса

### Template Service API

- `POST /api/template/render` - Обработка HTML-шаблона с подстановкой данных
- `GET /api/template/health` - Проверка работоспособности сервиса

### PDF Renderer API

- `POST /api/pdf/render` - Генерация PDF из HTML
- `GET /api/pdf/health` - Проверка работоспособности сервиса

### PNG Renderer API

- `POST /api/png/render` - Генерация PNG из HTML
- `GET /api/png/health` - Проверка работоспособности сервиса

## Примеры использования

### Пример шаблона с условными конструкциями

html

```html
<div class="document">
  <h1>{{ title }}</h1>
  <p>Дата создания: {{ date }}</p>
  
  {% if show_details %}
    <div class="details">
      <h2>Подробная информация</h2>
      <p>{{ details }}</p>
    </div>
  {% endif %}
  
  <div class="footer">
    <p>© {{ company }}</p>
  </div>
</div>
```

### Пример запроса на генерацию документа

json

```json
{
  "template_id": 1,
  "data": {
    "title": "Пример документа",
    "date": "2025-04-26",
    "show_details": true,
    "details": "Это подробная информация, которая отображается только при show_details=true",
    "company": "ООО Рога и Копыта"
  }
}
```

## Расширение системы

### Добавление нового формата документа

1. Создать новый сервис для рендеринга в нужный формат
2. Добавить поддержку нового формата в Render Routing Service
3. Обновить модели в Storage Service для хранения документов нового формата

### Расширение возможностей шаблонизации

Template Service построен на Jinja2, что позволяет легко расширять его возможности:

1. Добавление циклов: `{% for item in items %}...{% endfor %}`
2. Добавление фильтров: `{{ variable | filter }}`
3. Добавление макросов: `{% macro name(args) %}...{% endmacro %}`

## Разработка и отладка

### Логирование

Все сервисы настроены на подробное логирование. Логи доступны:

- В консоли контейнеров (`docker logs <container_name>`)
- В файлах логов внутри контейнеров
- Через стандартный вывод в Docker Compose

### Отладка

1. Для отладки Frontend: `docker-compose up frontend -d`
2. Для отладки backend-сервисов: `docker-compose up <service_name> -d`

### Тестирование

Для тестирования API можно использовать:

1. API документацию (Swagger/OpenAPI):
    - Template Service: `http://localhost/api/template/docs`
    - PNG Renderer: `http://localhost/api/png/docs`
2. Инструменты для тестирования API:
    - Postman
    - curl
    - httpie