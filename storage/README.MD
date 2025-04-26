## Обзор

Storage Service - это Django-приложение, отвечающее за хранение шаблонов документов и сгенерированных файлов. Сервис предоставляет REST API для управления шаблонами и доступа к сгенерированным документам.

## Архитектура

```
storage/
├── manage.py                    # Скрипт управления Django
├── requirements.txt             # Зависимости Python
├── Dockerfile                   # Инструкции для сборки Docker-образа
├── media/                       # Директория для хранения файлов
│   └── generated_templates/     # Сгенерированные документы
├── storage/                     # Основной пакет Django-проекта
│   ├── __init__.py
│   ├── asgi.py                  # Конфигурация ASGI
│   ├── settings.py              # Настройки проекта
│   ├── urls.py                  # Корневые URL-маршруты
│   └── wsgi.py                  # Конфигурация WSGI
└── templates/                   # Приложение для работы с шаблонами
    ├── __init__.py
    ├── admin.py                 # Настройки административного интерфейса
    ├── apps.py                  # Конфигурация приложения
    ├── middleware.py            # Middleware для API-ключей
    ├── migrations/              # Миграции базы данных
    ├── models.py                # Модели данных
    ├── serializers.py           # Сериализаторы для REST API
    ├── tests.py                 # Тесты
    ├── urls.py                  # URL-маршруты приложения
    └── views.py                 # Обработчики запросов
```

## Модели данных

### Template

Представляет шаблон документа.

**Поля**:

- `name` (TextField): Название шаблона
- `version` (TextField): Версия шаблона
- `type` (CharField): Тип шаблона (pdf, png, svg)

### Page

Представляет страницу шаблона.

**Поля**:

- `template` (ForeignKey): Связь с шаблоном
- `name` (TextField): Название страницы
- `html` (TextField): HTML-код страницы
- `width` (IntegerField): Ширина страницы
- `height` (IntegerField): Высота страницы
- `units` (CharField): Единицы измерения (mm, px)
- `bleeds` (IntegerField, опционально): Размер припусков для PDF

### Field

Представляет поле для подстановки данных в шаблон.

**Поля**:

- `page` (ForeignKey): Связь со страницей
- `name` (TextField): Имя поля (используется в плейсхолдерах)
- `label` (TextField): Отображаемое название поля
- `required` (BooleanField): Обязательность поля

### PageAsset

Представляет ассет (изображение, шрифт), связанный со страницей.

**Поля**:

- `page` (ForeignKey): Связь со страницей
- `file` (FileField): Файл ассета

### PageSettings

Представляет дополнительные настройки страницы.

**Поля**:

- `page` (ForeignKey): Связь со страницей
- `key` (CharField): Ключ настройки
- `value` (TextField): Значение настройки

### GeneratedTemplate

Представляет сгенерированный документ.

**Поля**:

- `template` (ForeignKey): Связь с шаблоном
- `file` (FileField): Сгенерированный файл
- `format` (CharField): Формат файла (pdf, png, svg)
- `created_at` (DateTimeField): Дата создания
- `data` (JSONField): Данные, использованные для генерации

## API-интерфейсы

### Получение списка шаблонов

**Запрос**:

```
GET /api/templates/
```

**Ответ**:

json

```json
[
  {
    "id": 1,
    "name": "Шаблон документа",
    "version": "1.0",
    "type": "pdf",
    "pages": [
      {
        "name": "Страница 1",
        "html": "<html>...</html>",
        "width": 210,
        "height": 297,
        "units": "mm",
        "bleeds": 3,
        "fields": [
          {
            "name": "title",
            "label": "Заголовок",
            "required": true
          }
        ],
        "assets": [
          {
            "file": "/media/page_assets/logo.png"
          }
        ]
      }
    ]
  }
]
```

### Получение конкретного шаблона

**Запрос**:

```
GET /api/templates/{id}/
```

**Ответ**: Аналогичен ответу на получение списка шаблонов, но содержит только один шаблон.

### Загрузка сгенерированного документа

**Запрос**:

```
POST /api/upload-template/
Content-Type: multipart/form-data

- file: [двоичные данные файла]
- template_id: 1
- format: "pdf"
- form_data: {"title": "Пример", ...}
```

**Ответ**:

json

```json
{
  "id": 1,
  "url": "/media/generated_templates/document_123.pdf",
  "format": "pdf",
  "created_at": "2025-04-26T14:30:00Z"
}
```

### Получение сгенерированного документа

**Запрос**:

```
GET /api/files/{id}/
```

**Ответ**: Файл документа с соответствующим Content-Type.

## Middleware

### ApiKeyMiddleware

Обеспечивает безопасность API, проверяя наличие и корректность API-ключа в заголовке запроса.

python

```python
class ApiKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Проверяем только защищенные API-запросы
        if request.path.startswith('/api/upload-template/'):
            api_key = request.headers.get('X-API-Key')
            if api_key != settings.API_KEY:
                return HttpResponseForbidden('Invalid API key')
        
        return self.get_response(request)
```

## Настройка и запуск

### Переменные окружения

- `DJANGO_DEBUG`: Режим отладки (True/False)
- `DJANGO_SECRET_KEY`: Секретный ключ Django
- `API_KEY`: Ключ для API-авторизации

### Команды для запуска

bash

```bash
# Миграция базы данных
python manage.py migrate

# Сбор статических файлов
python manage.py collectstatic --noinput

# Запуск сервера
gunicorn storage.wsgi:application --bind 0.0.0.0:8000
```

### Запуск через Docker

bash

```bash
docker build -t storage-service .
docker run -p 8000:8000 -e API_KEY=your-api-key storage-service
```

## Расширение функциональности

### Добавление нового типа шаблона

1. Добавить новый вариант в `TEMPLATE_TYPES` в модели `Template`
2. Создать соответствующие обработчики в `views.py`
3. Обновить сериализаторы в `serializers.py` при необходимости

### Добавление нового типа поля

1. Расширить модель `Field` новыми полями
2. Обновить сериализатор `FieldSerializer`
3. Адаптировать административный интерфейс в `admin.py`