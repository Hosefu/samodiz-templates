import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

# Загружаем .env файл
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-development-only-key')
DEBUG = os.environ.get('DEBUG', '1') == '1'
ALLOWED_HOSTS = ['*']

# Приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_yasg',
    'django_celery_beat',
    'channels',
    'reversion',
    
    # local apps
    'apps.common',
    'apps.users',
    'apps.templates',
    'apps.generation',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Добавляем наш middleware для логирования безопасности
    'apps.users.middleware.SecurityLoggingMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

AUTH_USER_MODEL = 'users.User'

# Валидаторы паролей
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'apps.users.validators.StrongPasswordValidator',
        'OPTIONS': {
            'min_length': 8,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_numbers': True,
            'require_special': True,
        }
    },
    {
        'NAME': 'apps.users.validators.EmailUsernamePasswordValidator',
    },
]

# База данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'samodesdb'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Redis/Celery
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')

CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/1'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/2'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    # Добавляем ограничение запросов
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'registration': '5/hour',  # ограничение для регистрации
    }
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# Настройки Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [f'redis://{REDIS_HOST}:{REDIS_PORT}/0'],
        },
    },
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Internationalization
LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Asset upload settings
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

# Frontend URL для сброса пароля
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

# Email settings
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'admin@samodesign.ru')

# Расширенные настройки логирования
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'security': {
            'format': '[SECURITY] {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'security_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/security.log'),
            'formatter': 'security',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        'security': {
            'handlers': ['console', 'security_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Создаем директорию для логов, если её нет
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True) 

# MinIO/S3 Storage settings
USE_S3_STORAGE = True

# MinIO Configuration
MINIO_ENDPOINT_URL = f"http://{os.environ.get('MINIO_ENDPOINT', 'minio:9000')}"
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'minioadmin123')
MINIO_SECURE = os.environ.get('MINIO_SECURE', 'False').lower() == 'true'
MINIO_REGION = os.environ.get('MINIO_REGION', 'eu-west-1')
MINIO_BUCKET_TEMPLATES = os.environ.get('MINIO_BUCKET_TEMPLATES', 'templates-assets')
MINIO_BUCKET_DOCUMENTS = os.environ.get('MINIO_BUCKET_DOCUMENTS', 'generated-documents')
MINIO_PUBLIC_URL = f"http://localhost/{MINIO_BUCKET_TEMPLATES}"

# После существующих MinIO настроек добавить:
# Публичный базовый URL для доступа к ассетам
# В продакшене будет домен, в разработке - localhost через nginx
MINIO_PUBLIC_BASE_URL = os.environ.get('MINIO_PUBLIC_BASE_URL', 'http://localhost')

# Для совместимости с существующим кодом
CEPH_ENDPOINT_URL = MINIO_ENDPOINT_URL
CEPH_ACCESS_KEY = MINIO_ACCESS_KEY
CEPH_SECRET_KEY = MINIO_SECRET_KEY
CEPH_BUCKET_NAME = MINIO_BUCKET_TEMPLATES
CEPH_PUBLIC_URL = MINIO_PUBLIC_URL 