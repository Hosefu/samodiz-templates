"""
URL-маршруты для API шаблонов.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.templates.api.views import (
    TemplateViewSet, PageViewSet, FieldViewSet, 
    AssetViewSet, TemplatePermissionViewSet
)
from apps.generation.api.views import GenerateDocumentView

# Создаем основной роутер
router = DefaultRouter()
router.register(r'', TemplateViewSet, basename='template')

# Создаем вложенные пути для доступа к ресурсам шаблона
template_nested_routes = [
    # Страницы шаблона
    path('<uuid:template_id>/pages/', PageViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='template-pages-list'),
    
    path('<uuid:template_id>/pages/<uuid:pk>/', PageViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='template-page-detail'),
    
    # Поля шаблона
    path('<uuid:template_id>/fields/', FieldViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='template-fields-list'),
    
    path('<uuid:template_id>/fields/<uuid:pk>/', FieldViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='template-field-detail'),
    
    # Ассеты шаблона
    path('<uuid:template_id>/assets/', AssetViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='template-assets-list'),
    
    path('<uuid:template_id>/assets/<uuid:pk>/', AssetViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }), name='template-asset-detail'),
    
    # Разрешения шаблона
    path('<uuid:template_id>/permissions/', TemplatePermissionViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='template-permissions-list'),
    
    path('<uuid:template_id>/permissions/<uuid:pk>/', TemplatePermissionViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='template-permission-detail'),
    
    # Генерация документа
    path('<uuid:template_id>/generate/', GenerateDocumentView.as_view(), name='template-generate'),
    
    # Получение полей для генерации
    path('<uuid:template_id>/fields-for-generation/', 
         GenerateDocumentView.as_view(http_method_names=['get']),
         name='template-generation-fields'),
]

urlpatterns = template_nested_routes + router.urls