# storage/templates/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .auth_views import CustomTokenObtainPairView, LogoutView, UserProfileView
from .views import TemplateViewSet, pages_list_create, page_detail, upload_page_asset, delete_page_asset, upload_template_file, serve_template_file, health_check

router = DefaultRouter()
router.register(r'templates', TemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
    
    # Авторизация
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
    
    # Существующие эндпоинты
    path('templates/', include(router.urls)),
    path('templates/<int:template_id>/pages/', pages_list_create, name='pages-list-create'),
    path('templates/<int:template_id>/pages/<str:page_id>/', page_detail, name='page-detail'),
    path('templates/<int:template_id>/pages/<str:page_id>/assets/', upload_page_asset, name='upload-page-asset'),
    path('templates/<int:template_id>/pages/<str:page_id>/assets/<int:asset_id>/', delete_page_asset, name='delete-page-asset'),
    path('upload-template/', upload_template_file, name='upload-template'),
    path('files/<int:file_id>/', serve_template_file, name='serve-template-file'),
    path('health/', health_check, name='health-check'),
]