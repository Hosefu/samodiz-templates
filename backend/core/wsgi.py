"""
WSGI конфигурация для Самодизайн проекта.

Этот файл используется для запуска с помощью Gunicorn или другого WSGI-сервера.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()