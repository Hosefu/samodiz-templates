"""
Представления API для аутентификации и управления пользователями.
"""
import logging
import uuid
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework import status, viewsets, mixins, generics
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User, ExtendedGroup
from apps.users.api.serializers import (
    CustomTokenObtainPairSerializer, RegisterSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    UserSerializer, UserDetailSerializer, GroupSerializer
)
from apps.users.api.permissions import IsSelfOrAdmin

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Аутентификация пользователя и получение JWT токенов.
    
    Возвращает access и refresh токены, а также информацию о пользователе.
    """
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """
    Обновление JWT токена.
    
    Использует refresh токен для получения нового access токена.
    """
    pass


class LogoutView(APIView):
    """
    Выход пользователя из системы.
    
    Аннулирует refresh токен.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Аннулирует refresh токен."""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                # Аннулируем токен
                token = RefreshToken(refresh_token)
                token.blacklist()
                
                return Response(
                    {"detail": "Успешный выход из системы."},
                    status=status.HTTP_200_OK
                )
            
            return Response(
                {"detail": "Необходимо предоставить refresh токен."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            return Response(
                {"detail": f"Ошибка при выходе из системы: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class RegisterView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class PasswordResetRequestView(APIView):
    """
    Запрос на сброс пароля.
    
    Отправляет электронное письмо с токеном для сброса пароля.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Обрабатывает запрос на сброс пароля."""
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Генерируем уникальный токен
                token = str(uuid.uuid4())
                
                # Сохраняем токен и время его создания в моделе пользователя
                # (для этого надо добавить поля password_reset_token и password_reset_token_created_at)
                user.password_reset_token = token
                user.password_reset_token_created_at = timezone.now()
                user.save(update_fields=['password_reset_token', 'password_reset_token_created_at'])
                
                # Формируем ссылку для сброса пароля
                reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}"
                
                # Отправляем письмо
                subject = "Сброс пароля"
                message = f"Перейдите по ссылке для сброса пароля: {reset_url}"
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                return Response(
                    {"detail": "Инструкции по сбросу пароля отправлены на указанный email."},
                    status=status.HTTP_200_OK
                )
            
            except User.DoesNotExist:
                # Для безопасности не сообщаем, что пользователь не существует
                return Response(
                    {"detail": "Инструкции по сбросу пароля отправлены на указанный email."},
                    status=status.HTTP_200_OK
                )
            
            except Exception as e:
                logger.error(f"Error sending password reset email: {e}")
                return Response(
                    {"detail": "Ошибка при отправке инструкций по сбросу пароля."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Подтверждение сброса пароля.
    
    Устанавливает новый пароль по токену сброса.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Обрабатывает подтверждение сброса пароля."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']
            
            try:
                # Находим пользователя по токену
                user = User.objects.get(password_reset_token=token)
                
                # Проверяем, не истек ли срок действия токена (24 часа)
                token_created_at = user.password_reset_token_created_at
                if token_created_at and (timezone.now() - token_created_at).days < 1:
                    # Устанавливаем новый пароль
                    user.set_password(password)
                    
                    # Очищаем токен сброса
                    user.password_reset_token = None
                    user.password_reset_token_created_at = None
                    
                    user.save()
                    
                    return Response(
                        {"detail": "Пароль успешно изменен."},
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {"detail": "Истек срок действия токена сброса пароля."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            except User.DoesNotExist:
                return Response(
                    {"detail": "Недействительный токен сброса пароля."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            except Exception as e:
                logger.error(f"Error resetting password: {e}")
                return Response(
                    {"detail": "Ошибка при сбросе пароля."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """API для управления пользователями."""
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]
    
    def get_queryset(self):
        """
        Возвращает список пользователей.
        
        Администраторы видят всех пользователей, обычные пользователи - только себя.
        """
        user = self.request.user
        
        if user.is_staff:
            return User.objects.all()
        
        return User.objects.filter(id=user.id)
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Возвращает информацию о текущем пользователе."""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)


class GroupViewSet(viewsets.ModelViewSet):
    """API для управления группами пользователей."""
    
    queryset = ExtendedGroup.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]