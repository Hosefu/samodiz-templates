"""
URL-маршруты для API шаблонов.
"""
from django.urls import path, include
from django.utils.module_loading import import_string
from rest_framework.routers import DefaultRouter
from apps.templates.api.views import (
    TemplateViewSet, PageViewSet, FieldViewSet, 
    AssetViewSet, TemplatePermissionViewSet, FieldChoiceViewSet
)

# Создаем основной роутер
router = DefaultRouter()
router.register(r'', TemplateViewSet, basename='template')

# Создаем вложенные пути для доступа к ресурсам шаблона
template_nested_routes = [
    # Страницы шаблона
    path('pages/', PageViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='template-pages-list'),
    
    path('pages/<uuid:pk>/', PageViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='template-page-detail'),
    
    # Поля шаблона
    path('fields/', FieldViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='template-fields-list'),
    
    path('fields/<uuid:pk>/', FieldViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='template-field-detail'),
    
    # Варианты выбора для полей
    path('fields/<uuid:field_id>/choices/', 
         FieldChoiceViewSet.as_view({
             'get': 'list',
             'post': 'create'
         }), 
         name='field-choices-list'),
    
    path('fields/<uuid:field_id>/choices/<uuid:pk>/', 
         FieldChoiceViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'partial_update',
             'delete': 'destroy'
         }), 
         name='field-choice-detail'),
    
    # Ассеты шаблона
    path('assets/', AssetViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='template-assets-list'),
    
    path('assets/<uuid:pk>/', AssetViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }), name='template-asset-detail'),
    
    # Разрешения шаблона
    path('permissions/', TemplatePermissionViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='template-permissions-list'),
    
    path('permissions/<uuid:pk>/', TemplatePermissionViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='template-permission-detail'),
    
    # Генерация документа
    path('generate/', import_string('apps.generation.api.views.GenerateDocumentViewSet').as_view({'post': 'generate'}), name='template-generate'),
    
    # Получение полей для генерации
    path('fields/', import_string('apps.generation.api.views.GenerateDocumentViewSet').as_view({'get': 'get_template_fields'}), name='template-get-fields'),
    
    # Закомментированный старый URL можно будет удалить позже, если новый подход работает
    # path('fields-for-generation/', 
    #      'apps.generation.api.views.GenerateDocumentView', # TODO: Разобраться как правильно указать http_method_names=['get'] или переделать
    #      name='template-generation-fields'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('<uuid:template_id>/', include(template_nested_routes)),
]