from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
import logging

# Configure logger
logger = logging.getLogger('auth_service')

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомный класс для получения JWT токенов с дополнительной информацией о пользователе"""
    
    def post(self, request, *args, **kwargs):
        try:
            logger.info(f"Login attempt for user: {request.data.get('username', 'unknown')}")
            
            # Проверяем наличие обязательных полей
            if not request.data.get('username'):
                logger.error("Username not provided in request")
                return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)
                
            if not request.data.get('password'):
                logger.error("Password not provided in request")
                return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            response = super().post(request, *args, **kwargs)
            
            # Если аутентификация успешна, добавляем информацию о пользователе
            if response.status_code == 200:
                user = User.objects.get(username=request.data['username'])
                logger.info(f"Login successful for user: {user.username}")
                response.data['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_admin': user.is_admin()
                }
            return response
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {'error': f'Authentication error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

class LogoutView(APIView):
    """Выход из системы - блокировка Refresh Token"""
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    """Получение и обновление профиля пользователя"""
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 