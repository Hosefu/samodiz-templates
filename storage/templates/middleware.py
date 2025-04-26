# storage/templates/middleware.py
from django.http import HttpResponseForbidden
from django.conf import settings

class ApiKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Проверяем только защищенные API-запросы
        if request.path.startswith('/api/') and request.method != 'GET':
            # Проверка разных вариантов заголовка API-ключа (с регистронезависимостью)
            api_key = None
            for header in ['X-API-Key', 'X-API-KEY', 'x-api-key']:
                if header in request.headers:
                    api_key = request.headers[header]
                    break
            
            if api_key != settings.API_KEY:
                # Выводим отладочную информацию
                print(f"Expected API key: {settings.API_KEY}")
                print(f"Received API key: {api_key}")
                print(f"Headers: {dict(request.headers)}")
                return HttpResponseForbidden('Invalid API key')
        
        return self.get_response(request)