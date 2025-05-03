"""
Продакшн настройки для проекта.
"""
import os
from .base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# База данных PostgreSQL для продакшена
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'samodesign'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# Настройки безопасности для продакшена
SECURE_HSTS_SECONDS = 31536000  # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS настройки для продакшена - только разрешенные домены
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')

# Логирование для продакшена
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
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

# В продакшене задачи Celery должны выполняться асинхронно
CELERY_TASK_ALWAYS_EAGER = False

# Продакшн настройки Ceph/S3 из переменных окружения
CEPH_ENDPOINT_URL = os.environ.get('CEPH_ENDPOINT_URL')
CEPH_ACCESS_KEY = os.environ.get('CEPH_ACCESS_KEY')
CEPH_SECRET_KEY = os.environ.get('CEPH_SECRET_KEY')
CEPH_BUCKET_NAME = os.environ.get('CEPH_BUCKET_NAME')
CEPH_REGION_NAME = os.environ.get('CEPH_REGION_NAME', '')

# Рендереры в продакшене
PDF_RENDERER_URL = os.environ.get('PDF_RENDERER_URL', 'http://pdf-renderer/api/render')
PNG_RENDERER_URL = os.environ.get('PNG_RENDERER_URL', 'http://png-renderer/api/render')
SVG_RENDERER_URL = os.environ.get('SVG_RENDERER_URL', 'http://svg-renderer/api/render')