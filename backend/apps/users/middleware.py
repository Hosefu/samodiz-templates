import logging
import json
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin

# Настройка логирования безопасности
security_logger = logging.getLogger('security')


class SecurityLoggingMiddleware(MiddlewareMixin):
    """
    Middleware для логирования действий, связанных с безопасностью.
    
    Отслеживает попытки авторизации, смены пароля и другие критичные операции.
    """
    
    AUTH_PATHS = [
        '/api/v1/auth/login/',
        '/api/v1/auth/token/refresh/',
        '/api/v1/auth/password/reset/',
        '/api/v1/auth/password/reset/confirm/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def process_request(self, request):
        """Обработка входящего запроса."""
        # Сохраняем время начала запроса
        request.start_time = datetime.now()
        return None
    
    def process_response(self, request, response):
        """Обработка исходящего ответа."""
        path = request.path
        
        # Логируем только интересующие нас пути
        if not any(path.startswith(auth_path) for auth_path in self.AUTH_PATHS):
            return response
        
        # Получаем данные запроса
        method = request.method
        status_code = response.status_code
        
        # Определяем статус запроса
        is_success = 200 <= status_code < 300
        
        # Получаем IP и User-Agent
        client_ip = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        # Получаем пользователя, если он авторизован
        user_info = "Anonymous"
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_info = f"user_id={request.user.id}, username={request.user.username}"
        
        # Подготавливаем данные для логирования
        log_data = {
            'path': path,
            'method': method,
            'status_code': status_code,
            'client_ip': client_ip,
            'user_agent': user_agent,
            'user': user_info,
            'timestamp': datetime.now().isoformat(),
        }
        
        # Время выполнения запроса
        if hasattr(request, 'start_time'):
            execution_time = (datetime.now() - request.start_time).total_seconds()
            log_data['execution_time'] = f"{execution_time:.4f}s"
        
        # Логируем попытки авторизации
        if path == '/api/v1/auth/login/':
            if is_success:
                security_logger.info(f"Successful login: {json.dumps(log_data)}")
            else:
                security_logger.warning(f"Failed login attempt: {json.dumps(log_data)}")
        
        # Логируем сброс пароля
        elif path.startswith('/api/v1/auth/password/reset'):
            if is_success:
                security_logger.info(f"Password reset action: {json.dumps(log_data)}")
            else:
                security_logger.warning(f"Failed password reset action: {json.dumps(log_data)}")
        
        return response
    
    def _get_client_ip(self, request):
        """Получение IP-адреса клиента с учетом прокси."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 