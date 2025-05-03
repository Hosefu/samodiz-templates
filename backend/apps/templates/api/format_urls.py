"""
URL-маршруты для API форматов документов.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.templates.api.views import FormatViewSet

# Создаем роутер для форматов
router = DefaultRouter()
router.register(r'', FormatViewSet, basename='format')

urlpatterns = router.urls