"""
Разрешения для API генерации документов.
"""
from rest_framework import permissions
from django.utils import timezone
from apps.generation.models import RenderTask, GeneratedDocument


class DocumentTokenOrAuthenticated(permissions.BasePermission):
    """
    Разрешение для доступа к документам:
    - Если есть токен и нет авторизации -> проверяем токен
    - Если нет токена и есть авторизация -> стандартная проверка
    - Если есть и то и другое -> отказ
    - Если нет ни токена ни авторизации -> отказ
    """
    
    def has_permission(self, request, view):
        # Получаем токен из query параметров или заголовков
        token = request.query_params.get('document_token') or request.headers.get('X-Document-Token')
        is_authenticated = request.user and request.user.is_authenticated
        
        # Если есть и токен и авторизация -> отказ
        if token and is_authenticated:
            return False
        
        # Если нет ни токена ни авторизации -> отказ
        if not token and not is_authenticated:
            return False
        
        # Если есть только авторизация -> проверяем как обычно
        if is_authenticated and not token:
            return True
        
        # Если есть только токен -> сохраняем его для дальнейшей проверки
        if token and not is_authenticated:
            request.document_token = token
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Если это документ, проверяем доступ по токену или владельцу
        if isinstance(obj, GeneratedDocument):
            return self._check_document_access(request, obj)
        
        # Если это задача, проверяем доступ по токену или владельцу
        if isinstance(obj, RenderTask):
            return self._check_task_access(request, obj)
        
        return True
    
    def _check_document_access(self, request, document):
        # Если есть токен документа
        if hasattr(request, 'document_token'):
            task = document.task
            return (
                task.document_token == request.document_token and
                task.document_token_expires_at and
                task.document_token_expires_at > timezone.now()
            )
        
        # Если авторизован, проверяем владение
        if request.user and request.user.is_authenticated:
            return document.task.user == request.user or request.user.is_staff
        
        return False
    
    def _check_task_access(self, request, task):
        # Если есть токен документа
        if hasattr(request, 'document_token'):
            return (
                task.document_token == request.document_token and
                task.document_token_expires_at and
                task.document_token_expires_at > timezone.now()
            )
        
        # Если авторизован, проверяем владение
        if request.user and request.user.is_authenticated:
            return task.user == request.user or request.user.is_staff
        
        return False 