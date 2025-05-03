"""
Локальные настройки для разработки.
"""
import os
from .base import *  # noqa

DEBUG = True

# База данных PostgreSQL для локальной разработки в Docker
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'samodesdb'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Отключение HTTPS в разработке
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Добавляем DRF Browsable API для удобства разработки
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
)

# Подробное логирование для разработки
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

# В разработке используем синхронные задачи Celery
CELERY_TASK_ALWAYS_EAGER = True

# Локальные URL для рендереров
PDF_RENDERER_URL = 'http://localhost:8001/api/render'
PNG_RENDERER_URL = 'http://localhost:8002/api/render'
SVG_RENDERER_URL = 'http://localhost:8003/api/render'

# Добавляем Django Debug Toolbar
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    INTERNAL_IPS = ['127.0.0.1']