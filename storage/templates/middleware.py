# storage/templates/middleware.py
from django.http import HttpResponseForbidden
from django.conf import settings

class ApiKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Проверяем только защищенные API-запросы
        if request.path.startswith('/api/upload-template/'):
            api_key = request.headers.get('X-API-Key')
            if api_key != settings.API_KEY:
                return HttpResponseForbidden('Invalid API key')
        
        return self.get_response(request)