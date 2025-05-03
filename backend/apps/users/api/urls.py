"""
URL-маршруты для API аутентификации.
"""
from django.urls import path
from apps.users.api.views import (
    CustomTokenObtainPairView, CustomTokenRefreshView, LogoutView,
    RegisterView, PasswordResetRequestView, PasswordResetConfirmView
)

urlpatterns = [
    # Аутентификация
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Регистрация и сброс пароля
    path('register/', RegisterView.as_view(), name='register'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]