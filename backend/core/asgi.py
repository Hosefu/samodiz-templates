"""
ASGI конфигурация для Самодизайн проекта.

Этот файл поддерживает как HTTP, так и WebSocket соединения.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from apps.templates.consumers import TemplateRenderConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.base')

# Получаем стандартный Django ASGI application
django_asgi_app = get_asgi_application()

# Настраиваем маршрутизацию для разных протоколов
application = ProtocolTypeRouter({
    # HTTP
    "http": django_asgi_app,
    
    # WebSocket с поддержкой аутентификации
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/templates/<int:template_id>/render/', TemplateRenderConsumer.as_asgi()),
        ])
    ),
})