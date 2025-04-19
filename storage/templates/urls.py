from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TemplateViewSet, upload_template_file, serve_template_file

router = DefaultRouter()
router.register(r'templates', TemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
    path('upload-template/', upload_template_file, name='upload-template'),
    path('file/<int:file_id>/', serve_template_file, name='serve-template-file'),
]