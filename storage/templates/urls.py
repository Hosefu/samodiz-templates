from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TemplateViewSet, upload_pdf

router = DefaultRouter()
router.register(r'templates', TemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
    path('upload-pdf/', upload_pdf, name='upload-pdf'),  # новый URL
]