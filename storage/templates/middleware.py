from django.http import HttpResponseForbidden
from django.conf import settings

class ApiKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Проверяем только запросы к API загрузки PDF
        if request.path.startswith('/api/upload-pdf/'):
            api_key = request.headers.get('X-API-Key')
            if api_key != settings.API_KEY:
                return HttpResponseForbidden('Недопустимый API-ключ')
        
        return self.get_response(request)