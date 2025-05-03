"""
URL-маршруты для API групп пользователей.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.api.views import GroupViewSet

# Создаем роутер для групп
router = DefaultRouter()
router.register(r'', GroupViewSet, basename='group')

urlpatterns = router.urls