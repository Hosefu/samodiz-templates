## Обзор

Render Routing Service - это сервис на Go, который выполняет роль маршрутизатора запросов на рендеринг документов. Он получает запросы на генерацию документов, извлекает шаблоны из Storage Service, обрабатывает их с помощью Template Service и отправляет в соответствующие рендереры.

## Архитектура

```
render-routing/
├── cmd/
│   └── server/
│       └── main.go              # Точка входа приложения
├── internal/
│   ├── api/
│   │   ├── handlers.go          # Обработчики HTTP-запросов
│   │   └── routes.go            # Маршруты API
│   ├── config/
│   │   └── config.go            # Конфигурация сервиса
│   ├── models/
│   │   ├── request.go           # Модели запросов
│   │   ├── response.go          # Модели ответов
│   │   └── template.go          # Модели шаблонов
│   ├── renderer/
│   │   ├── client.go            # Клиент для взаимодействия с рендерерами
│   │   ├── router.go            # Маршрутизация запросов к рендерерам
│   │   └── template_processor.go # Обработка шаблонов
│   ├── storage/
│   │   └── client.go            # Клиент для взаимодействия с Storage Service
│   └── template/
│       └── client.go            # Клиент для взаимодействия с Template Service
├── pkg/
│   ├── httputil/
│   │   └── client.go            # Утилиты для HTTP-запросов
│   ├── logger/
│   │   └── logger.go            # Логирование
│   └── unitconv/
│       └── unitconv.go          # Конвертация единиц измерения
├── Dockerfile                   # Инструкции для сборки Docker-образа
├── go.mod                       # Зависимости Go
└── go.sum                       # Контрольные суммы зависимостей
```

## Компоненты

### Main (cmd/server/main.go)

Точка входа приложения. Инициализирует конфигурацию, логирование, клиенты для взаимодействия с другими сервисами и запускает HTTP-сервер.

**Ключевые функции**:

- Загрузка конфигурации из файла или переменных окружения
- Инициализация логирования
- Создание HTTP-клиентов для сервисов
- Настройка маршрутизатора API
- Запуск HTTP-сервера
- Обработка сигналов для корректного завершения

### API (internal/api)

Определяет HTTP-маршруты и обработчики запросов.

**Ключевые функции**:

- `RenderDocument`: Обработка запросов на рендеринг документа
- `GetRenderStatus`: Получение статуса рендеринга
- `HealthCheck`: Проверка работоспособности сервиса
- `NotFound`: Обработка запросов к несуществующим маршрутам

### Config (internal/config)

Определяет структуры для хранения конфигурации приложения.

**Ключевые структуры**:

- `Config`: Основная конфигурация
- `ServerConfig`: Настройки HTTP-сервера
- `RenderersConfig`: URL-адреса сервисов рендеринга
- `StorageAPIConfig`: Настройки для Storage Service
- `TemplateServiceConfig`: Настройки для Template Service
- `HTTPClientConfig`: Настройки HTTP-клиентов
- `LoggerConfig`: Настройки логирования

### Models (internal/models)

Определяет структуры данных для запросов, ответов и шаблонов.

**Ключевые структуры**:

- `RenderRequest`: Запрос на рендеринг документа
- `RenderResponse`: Ответ на запрос рендеринга
- `RendererRequest`: Запрос к сервису рендеринга
- `RendererResponse`: Ответ от сервиса рендеринга
- `StorageUploadRequest`: Запрос на загрузку файла в Storage Service
- `Template`: Шаблон документа
- `TemplatePage`: Страница шаблона

### Renderer (internal/renderer)

Реализует логику маршрутизации запросов к соответствующим рендерерам.

**Ключевые компоненты**:

- `Client`: Клиент для взаимодействия с рендерерами
- `Router`: Маршрутизатор запросов к рендерерам
- `TemplateProcessor`: Обработка шаблонов перед рендерингом

### Storage (internal/storage)

Реализует взаимодействие с Storage Service.

**Ключевые функции**:

- `GetTemplate`: Получение шаблона из Storage Service
- `UploadGeneratedFile`: Загрузка сгенерированного файла в Storage Service

### Template (internal/template)

Реализует взаимодействие с Template Service.

**Ключевые функции**:

- `RenderTemplate`: Отправка запроса на обработку шаблона в Template Service

### HTTP Utilities (pkg/httputil)

Предоставляет утилиты для выполнения HTTP-запросов.

**Ключевые функции**:

- `Get`: Выполнение GET-запроса
- `Post`: Выполнение POST-запроса с JSON-данными
- `PostMultipart`: Выполнение POST-запроса с multipart-данными

### Logger (pkg/logger)

Предоставляет интерфейс для логирования.

**Ключевые функции**:

- `Debug`, `Info`, `Warn`, `Error`, `Fatal`: Логирование сообщений разных уровней
- `With`: Добавление полей к логгеру
- `WithField`: Добавление одного поля к логгеру

### Unit Conversion (pkg/unitconv)

Предоставляет функции для конвертации единиц измерения.

**Ключевые функции**:

- `MillimetersToPixels`: Конвертация миллиметров в пиксели
- `PixelsToMillimeters`: Конвертация пикселей в миллиметры
- `PointsToPixels`: Конвертация пунктов в пиксели
- `MillimetersToPoints`: Конвертация миллиметров в пункты

## Рабочий процесс

1. Клиент отправляет запрос на генерацию документа на `/api/render/generate`
2. Обработчик `GenerateDocument` в `handlers.go` проверяет запрос и передает его в `Router`
3. `Router` в `router.go` выполняет следующие действия:
    - Получает шаблон из Storage Service с помощью `storageClient.GetTemplate`
    - Отправляет шаблон в Template Service с помощью `templateClient.RenderTemplate`
    - Определяет тип шаблона и вызывает соответствующий обработчик (`handlePdfRendering` или `handlePngRendering`)
    - Отправляет обработанный HTML в соответствующий рендерер
    - Загружает результат в Storage Service с помощью `storageClient.UploadGeneratedFile`
    - Возвращает URL сгенерированного документа

## API-интерфейсы

### Генерация документа

**Запрос**:

```
POST /api/render/generate
Content-Type: application/json

{
  "template_id": 1,
  "data": {
    "title": "Пример документа",
    "date": "2025-04-26",
    "show_details": true,
    "details": "Подробная информация",
    "company": "ООО Рога и Копыта"
  },
  "generate_preview": true
}
```

**Ответ**:

json

```json
{
  "url": "/media/generated_templates/document_123.pdf",
  "format": "pdf",
  "created_at": "2025-04-26T14:30:00Z",
  "preview_url": "/media/generated_templates/document_123_preview.png"
}
```

### Проверка работоспособности

**Запрос**:

```
GET /api/health
```

**Ответ**:

json

```json
{
  "status": "ok",
  "service": "render-routing"
}
```

## Настройка и запуск

### Переменные окружения

- `SERVER_PORT`: Порт для HTTP-сервера
- `RENDERERS_PDF_RENDERER`: URL PDF-рендерера
- `RENDERERS_PNG_RENDERER`: URL PNG-рендерера
- `STORAGE_API_BASE_URL`: Базовый URL Storage Service
- `STORAGE_API_KEY`: API-ключ для Storage Service
- `TEMPLATE_SERVICE_URL`: URL Template Service
- `LOGGER_LEVEL`: Уровень логирования

### Запуск через Docker

bash

```bash
docker build -t render-routing-service .
docker run -p 8080:8080 \
  -e SERVER_PORT=8080 \
  -e RENDERERS_PDF_RENDERER=http://pdf-renderer:8081/api/pdf/render \
  -e RENDERERS_PNG_RENDERER=http://png-renderer:8082/api/png/render \
  -e STORAGE_API_BASE_URL=http://storage-service:8000/api \
  -e STORAGE_API_KEY=your-api-key \
  -e TEMPLATE_SERVICE_URL=http://template-service:8083/api/template/render \
  render-routing-service
```

## Расширение функциональности

### Добавление нового типа рендерера

1. Обновить `router.go`, добавив новый обработчик (например, `handleSvgRendering`)
2. Обновить `client.go` в пакете `renderer`, добавив новый метод (например, `RenderSVG`)
3. Обновить конфигурацию в `config.go`, добавив URL нового рендерера
4. Обновить маршрутизацию в `router.go`, добавив обработку нового типа шаблонов