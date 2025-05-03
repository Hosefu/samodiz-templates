"""
URL-маршруты для API документов.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.generation.api.views import DocumentViewSet

# Создаем роутер для документов
router = DefaultRouter()
router.register(r'', DocumentViewSet, basename='document')

urlpatterns = router.urls