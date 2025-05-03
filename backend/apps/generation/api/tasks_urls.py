"""
URL-маршруты для API задач рендеринга.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.generation.api.views import RenderTaskViewSet

# Создаем роутер для задач рендеринга
router = DefaultRouter()
router.register(r'', RenderTaskViewSet, basename='task')

urlpatterns = router.urls