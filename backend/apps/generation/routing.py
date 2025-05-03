"""
Маршрутизация WebSocket соединений для отслеживания прогресса генерации.
"""
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/tasks/<uuid:task_id>/stream/', consumers.TaskProgressConsumer.as_asgi()),
]