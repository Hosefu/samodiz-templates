"""
URL-маршруты для API единиц измерения.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.templates.api.views import UnitViewSet

# Создаем роутер для единиц измерения
router = DefaultRouter()
router.register(r'', UnitViewSet, basename='unit')

urlpatterns = router.urls