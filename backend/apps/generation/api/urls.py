"""
URL-маршруты для API генерации документов.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.generation.api.views import (
    RenderTaskViewSet, DocumentViewSet, GenerateDocumentViewSet
)

# Создаем маршруты
router = DefaultRouter()
router.register(r'tasks', RenderTaskViewSet, basename='render-task')
router.register(r'documents', DocumentViewSet, basename='document')

# Дополнительные маршруты для генерации
urlpatterns = [
    path('', include(router.urls)),
    path('templates/<uuid:template_id>/generate/', 
         GenerateDocumentViewSet.as_view({'post': 'generate'}),
         name='template-generate'),
    path('templates/<uuid:template_id>/fields/', 
         GenerateDocumentViewSet.as_view({'get': 'get_template_fields'}),
         name='template-generation-fields'),
] 