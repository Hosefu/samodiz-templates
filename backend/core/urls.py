"""
Основные URL-маршруты проекта.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Настройка Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="Самодизайн API",
        default_version='v1',
        description="API для системы генерации документов 'Самодизайн'",
        contact=openapi.Contact(email="admin@samodesign.ru"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Базовые URL для API
api_v1_urls = [
    path('auth/', include('apps.users.api.urls')),
    path('users/', include('apps.users.api.user_urls')),
    path('groups/', include('apps.users.api.group_urls')),
    path('units/', include('apps.templates.api.unit_urls')),
    path('formats/', include('apps.templates.api.format_urls')),
    path('templates/', include('apps.templates.api.template_urls')),
    path('tasks/', include('apps.generation.api.task_urls')),
    path('documents/', include('apps.generation.api.document_urls')),
    
    # Служебные эндпоинты
    path('health/', include('apps.common.api.health_urls')),
    path('ready/', include('apps.common.api.ready_urls')),
    path('metrics/', include('apps.common.api.metrics_urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include(api_v1_urls)),
    
    # Swagger/OpenAPI
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('openapi.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# Настройки для отладочного режима
if settings.DEBUG:
    from django.conf.urls.static import static
    
    # Добавляем auth urls для browsable API в разработке
    urlpatterns += [
        path('api-auth/', include('rest_framework.urls')),
    ]
    
    # Добавляем обслуживание статических файлов
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)