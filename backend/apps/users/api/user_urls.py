"""
URL-маршруты для API пользователей.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.api.views import UserViewSet

# Создаем роутер для пользователей
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = router.urls