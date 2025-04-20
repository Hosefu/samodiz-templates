# storage/templates/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TemplateViewSet, upload_template_file, serve_template_file, health_check

router = DefaultRouter()
router.register(r'templates', TemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
    path('templates/', include(router.urls)),  # Списки и детали шаблонов
    path('templates/<int:template_id>/render/', upload_template_file, name='render-template'),
    path('upload-template/', upload_template_file, name='upload-template'),
    path('files/<int:file_id>/', serve_template_file, name='serve-template-file'),
    path('health/', health_check, name='health-check'),
]