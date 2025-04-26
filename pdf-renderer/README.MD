## Обзор

PDF Renderer - это сервис на базе .NET, который генерирует PDF-документы из HTML. Сервис использует библиотеку iText7 для конвертации HTML в PDF и предоставляет REST API для взаимодействия с другими компонентами системы.

## Архитектура

```
pdf-renderer/
├── Controllers/
│   └── PdfController.cs         # Контроллер для генерации PDF и проверки работоспособности
├── Models/
│   ├── PdfRequest.cs            # Модель запроса на генерацию PDF
│   ├── PdfRequestValidator.cs   # Валидатор запросов
│   └── RenderResult.cs          # Модель результата рендеринга
├── Services/
│   ├── Interfaces.cs            # Интерфейсы сервисов
│   ├── PdfRenderService.cs      # Сервис рендеринга PDF
│   ├── PreviewService.cs        # Сервис генерации превью
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

### Models

#### PdfRequest

Упрощенная модель запроса на генерацию PDF.

**Поля**:

- `Html`: HTML-содержимое для рендеринга
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
3. Сервис конвертирует размеры страницы в пункты
4. Рендерит HTML в PDF с помощью iText7
5. Если запрошено превью, генерирует PNG-превью
6. Возвращает PDF-документ или URL превью с соответствующими заголовками

## API-интерфейсы

### Генерация PDF

**Запрос**:

```
POST /api/pdf/render
Content-Type: application/json

{
  "html": "<html><body><h1>Заголовок</h1><p>Содержание</p></body></html>",
  "width": 210,
  "height": 297,
  "units": "mm",
  "bleeds": 3,
  "generatePreview": false,
  "settings": {
    "compression": "true"
  }
}
```

**Ответ**: PDF-документ с соответствующим Content-Type или информация об ошибке в формате JSON.

### Проверка работоспособности

**Запрос**:

```
GET /api/pdf/health
```

**Ответ**:

```json
{
  "status": "ok",
  "service": "pdf-renderer"
}
```

## Обработка шрифтов и ассетов

PDF Renderer поддерживает пользовательские шрифты:

1. Шрифты загружаются из директорий:
    - Директория `assets` в `baseUri`
    - Стандартные шрифты iText (если пользовательские шрифты не найдены)

## Настройка и запуск

### Переменные окружения

- `ASPNETCORE_ENVIRONMENT`: Окружение (.NET (Development, Production))
- `ASPNETCORE_URLS`: URL для прослушивания (например, "http://+:8081")
- `Logging__LogLevel__Default`: Уровень логирования по умолчанию
- `Logging__LogLevel__PdfRenderer`: Уровень логирования для PdfRenderer