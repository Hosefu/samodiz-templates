"""
Локальные настройки для разработки.
"""
from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ['*']

# Отключение HTTPS в разработке
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Добавляем DRF Browsable API для удобства разработки
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
)

# Настройки для удобства отладки
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# В разработке используем синхронные задачи Celery для удобства отладки
CELERY_TASK_ALWAYS_EAGER = True

# CORS разрешаем в разработке все источники
CORS_ALLOW_ALL_ORIGINS = True

# Для локальной разработки используем Minio вместо Ceph
CEPH_ENDPOINT_URL = 'http://localhost:9000'
CEPH_ACCESS_KEY = 'minioadmin'
CEPH_SECRET_KEY = 'minioadmin'

# Локальные URL для рендереров в разработке
PDF_RENDERER_URL = 'http://localhost:8001/api/render'
PNG_RENDERER_URL = 'http://localhost:8002/api/render'
SVG_RENDERER_URL = 'http://localhost:8003/api/render'