# storage/templates/middleware.py
from django.http import HttpResponseForbidden
from django.conf import settings
import logging

logger = logging.getLogger('api_middleware')

class ApiKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Проверяем только защищенные API-запросы для межсервисного взаимодействия
        # Требуем API ключ только для запросов к сервисным API, не для запросов от фронтенда
        
        # Разрешаем все запросы к эндпоинтам, с которыми работает фронтенд
        if request.path.startswith('/api/auth/') or request.path.startswith('/api/templates/'):
            return self.get_response(request)
        
        # Для запросов к сервисным API (не от фронтенда) требуем API ключ
        # Например, для рендеринга, генерации PDF и т.д.
        if request.path.startswith('/api/render/') or request.path.startswith('/api/upload-template/'):
            # Проверка разных вариантов заголовка API-ключа (с регистронезависимостью)
            api_key = None
            for header in ['X-API-Key', 'X-API-KEY', 'x-api-key']:
                if header in request.headers:
                    api_key = request.headers[header]
                    break
            
            if api_key != settings.API_KEY:
                # Выводим отладочную информацию
                logger.error(f"Expected API key: {settings.API_KEY}")
                logger.error(f"Received API key: {api_key}")
                logger.debug(f"Headers: {dict(request.headers)}")
                return HttpResponseForbidden('Invalid API key')
        
        return self.get_response(request)