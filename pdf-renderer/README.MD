## Обзор

PDF Renderer - это сервис на базе .NET, который генерирует PDF-документы из HTML-шаблонов. Сервис использует библиотеку iText7 для конвертации HTML в PDF и предоставляет REST API для взаимодействия с другими компонентами системы.

## Архитектура

```
pdf-renderer/
├── Controllers/
│   ├── HealthController.cs      # Контроллер для проверки работоспособности
│   └── PdfController.cs         # Контроллер для генерации PDF
├── Models/
│   ├── PdfRequest.cs            # Модель запроса на генерацию PDF
│   ├── PdfRequestValidator.cs   # Валидатор запросов
│   ├── RenderResult.cs          # Модель результата рендеринга
│   └── TemplateMeta.cs          # Модель метаданных шаблона
├── Services/
│   ├── Interfaces.cs            # Интерфейсы сервисов
│   ├── PdfRenderService.cs      # Сервис рендеринга PDF
│   ├── PreviewService.cs        # Сервис генерации превью
│   ├── RazorTemplateService.cs  # Сервис обработки шаблонов с Razor
│   ├── TemplateCacheService.cs  # Сервис кэширования шаблонов
│   └── ValidationService.cs     # Сервис валидации запросов
├── Utils/
│   └── UnitConverter.cs         # Утилиты для конвертации единиц измерения
├── Program.cs                   # Точка входа приложения
├── appsettings.json             # Конфигурация приложения
├── appsettings.Development.json # Конфигурация для разработки
└── pdf-renderer.csproj          # Файл проекта .NET
```

## Компоненты

### Controllers

#### PdfController

Контроллер для обработки запросов на генерацию PDF.

**Ключевые методы**:

- `Render`: Обработка запросов на рендеринг PDF
- `HealthCheck`: Проверка работоспособности сервиса

#### HealthController

Контроллер для проверки работоспособности сервиса.

**Ключевые методы**:

- `HealthCheck`: Проверка работоспособности сервиса

### Models

#### PdfRequest

Модель запроса на генерацию PDF.

**Поля**:

- `Html`: HTML-содержимое для рендеринга
- `Data`: Данные для подстановки в шаблон
- `Width`: Ширина страницы
- `Height`: Высота страницы
- `Units`: Единицы измерения (px, mm)
- `Bleeds`: Размер припусков
- `GeneratePreview`: Генерировать ли превью
- `Settings`: Дополнительные настройки

#### PdfRequestValidator

Валидатор запросов на генерацию PDF.

**Правила валидации**:

- `Html`: Не должен быть пустым
- `Width`: Должен быть положительным
- `Height`: Должен быть положительным
- `Units`: Должен быть "mm" или "px"
- `Bleeds`: Не должен быть отрицательным

#### RenderResult

Модель результата рендеринга PDF.

**Поля**:

- `PreviewUrl`: URL превью (если было запрошено)
- `Error`: Сообщение об ошибке (если есть)

#### TemplateMeta

Модель метаданных шаблона.

**Поля**:

- `Id`: Идентификатор шаблона
- `Name`: Название шаблона
- `Version`: Версия шаблона
- `Pages`: Список страниц шаблона

### Services

#### PdfRenderService

Сервис для рендеринга PDF из HTML.

**Ключевые методы**:

- `RenderPdf`: Конвертация HTML в PDF
- `CreateConverterProperties`: Создание настроек конвертации

#### PreviewService

Сервис для генерации превью PDF-документов.

**Ключевые методы**:

- `GeneratePreviewAsync`: Генерация PNG-превью из PDF

#### RazorTemplateService

Сервис для обработки шаблонов с использованием Razor.

**Ключевые методы**:

- `RenderPage`: Рендеринг страницы с подстановкой данных

#### TemplateCacheService

Сервис для кэширования шаблонов.

**Ключевые методы**:

- `GetTemplateAsync`: Получение шаблона из кэша или Storage Service
- `CacheTemplateFromApiAsync`: Кэширование шаблона из API

#### ValidationService

Сервис для валидации запросов.

**Ключевые методы**:

- `Validate`: Валидация запроса на рендеринг PDF

### Utils

#### UnitConverter

Утилиты для конвертации единиц измерения.

**Ключевые методы**:

- `ConvertToPoints`: Конвертация в пункты
- `MillimetersToPoints`: Конвертация миллиметров в пункты
- `PixelsToPoints`: Конвертация пикселей в пункты

### Program.cs

Точка входа приложения. Настраивает сервисы, middleware и запускает HTTP-сервер.

**Ключевые настройки**:

- Регистрация сервисов в DI-контейнере
- Настройка CORS
- Настройка логирования
- Настройка маршрутизации

## Рабочий процесс

1. Клиент отправляет запрос на генерацию PDF на `/api/pdf/render`
2. `PdfController.Render` проверяет запрос и извлекает параметры
3. Если запрос содержит `template_id`, сервис получает шаблон из кэша или Storage Service
4. Для каждой страницы шаблона:
    - Настраивает baseUri для доступа к ассетам
    - Конвертирует размеры страницы в пункты
    - Рендерит HTML в PDF с помощью iText7
5. Если шаблон многостраничный, объединяет все страницы в один PDF
6. Если запрошено превью, генерирует PNG-превью
7. Возвращает PDF-документ с соответствующими заголовками

## API-интерфейсы

### Генерация PDF

**Запрос**:

```
POST /api/pdf/render
Content-Type: application/json

{
  "pages": [
    {
      "html": "<html><body><h1>Заголовок</h1><p>Содержание</p></body></html>",
      "width": 210,
      "height": 297,
      "units": "mm",
      "bleeds": 3,
      "settings": {
        "compression": "true"
      }
    }
  ],
  "template_id": 1,
  "generate_preview": true
}
```

**Ответ**: PDF-документ с соответствующим Content-Type или информация об ошибке в формате JSON.

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
  "service": "pdf-renderer"
}
```

## Обработка шрифтов и ассетов

PDF Renderer поддерживает пользовательские шрифты и ассеты:

1. Шрифты загружаются из директорий:
    - `/app/wwwroot/fonts`
    - Директория `assets` в `baseUri` шаблона
    - Системные директории шрифтов в Linux
2. Ассеты (изображения) загружаются из:
    - URL, указанных в HTML
    - `baseUri` шаблона

## Настройка и запуск

### Переменные окружения

- `ASPNETCORE_ENVIRONMENT`: Окружение (.NET (Development, Production))
- `ASPNETCORE_URLS`: URL для прослушивания (например, "http://+:8081")
- `Logging__LogLevel__Default`: Уровень логирования по умолчанию
- `Logging__LogLevel__PdfRenderer`: Уровень логирования для PdfRenderer

### Запуск через Docker

bash

```bash
docker build -t pdf-renderer .
docker run -p 8081:8081 \
  -e ASPNETCORE_ENVIRONMENT=Production \
  -e ASPNETCORE_URLS=http://+:8081 \
  pdf-renderer
```

### Запуск локально

bash

```bash
dotnet run --urls=http://localhost:8081
```

## Расширение функциональности

### Добавление новых форматов страниц

1. Расширить `UnitConverter.cs` для поддержки новых единиц измерения
2. Обновить валидатор в `PdfRequestValidator.cs`
3. Адаптировать `PdfRenderService.cs` для работы с новыми форматами

### Добавление поддержки дополнительных возможностей PDF

1. Расширить `PdfRenderService.cs` для настройки дополнительных параметров PDF
2. Добавить новые поля в `PdfRequest.cs`
3. Обновить `PdfRequestValidator.cs` для валидации новых полей