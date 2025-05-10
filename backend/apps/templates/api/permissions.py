"""
Классы разрешений для API шаблонов.
"""
from rest_framework import permissions
from apps.templates.models.template import Template, TemplatePermission


class IsTemplateOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение для шаблонов: только владелец может редактировать.
    
    Позволяет GET, HEAD и OPTIONS всем аутентифицированным пользователям,
    но требует владения шаблоном для остальных методов.
    """
    
    def has_permission(self, request, view):
        """Проверка базовых разрешений."""
        # Разрешаем GET, HEAD, OPTIONS для всех пользователей (включая анонимных)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Для остальных методов требуется аутентификация
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Для создания нового шаблона требуется аутентификация
        if view.action == 'create':
            return True
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """Проверка разрешений для конкретного объекта."""
        # Разрешаем GET, HEAD, OPTIONS для публичных шаблонов
        if request.method in permissions.SAFE_METHODS:
            if obj.is_public:
                return True
            
            # Для непубличных шаблонов проверяем аутентификацию
            if not request.user or not request.user.is_authenticated:
                return False
            
            if obj.owner == request.user:
                return True
            
            # Проверяем наличие разрешения на шаблон
            return TemplatePermission.objects.filter(
                template=obj,
                grantee=request.user
            ).exists()
        
        # Для остальных методов требуется аутентификация
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Изменять и удалять может только владелец или администратор
        return obj.owner == request.user or request.user.is_staff


class IsTemplateContributor(permissions.BasePermission):
    """
    Разрешение для редактирования содержимого шаблона.
    
    Позволяет редактировать контент шаблона владельцам и редакторам.
    """
    
    def has_permission(self, request, view):
        """Проверка базовых разрешений."""
        # Только аутентифицированные пользователи
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Получаем ID шаблона из URL
        template_id = view.kwargs.get('template_id')
        if not template_id:
            return False
        
        try:
            template = Template.objects.get(id=template_id)
            
            # Владелец и администраторы имеют полный доступ
            if template.owner == request.user or request.user.is_staff:
                return True
            
            # Проверяем наличие разрешения уровня editor или owner
            if request.method in permissions.SAFE_METHODS:
                # Для чтения достаточно любого доступа
                return (
                    template.is_public or 
                    TemplatePermission.objects.filter(
                        template=template,
                        grantee=request.user
                    ).exists()
                )
            else:
                # Для изменения требуется уровень editor или owner
                return TemplatePermission.objects.filter(
                    template=template,
                    grantee=request.user,
                    role__in=['editor', 'owner']
                ).exists()
        
        except Template.DoesNotExist:
            return False


class IsTemplateViewerOrBetter(permissions.BasePermission):
    """
    Разрешение для просмотра шаблона.
    
    Позволяет просматривать шаблон владельцам, редакторам и зрителям.
    """
    
    def has_permission(self, request, view):
        """Проверка базовых разрешений."""
        # Получаем ID шаблона из URL
        template_id = view.kwargs.get('pk') or view.kwargs.get('template_id')
        if not template_id:
            return False
        
        try:
            template = Template.objects.get(id=template_id)
            
            # Публичные шаблоны доступны всем
            if template.is_public:
                return True
            
            # Для непубличных шаблонов требуется аутентификация
            if not request.user or not request.user.is_authenticated:
                return False
            
            # Владелец и администраторы имеют полный доступ
            if template.owner == request.user or request.user.is_staff:
                return True
            
            # Проверяем наличие любого разрешения
            return TemplatePermission.objects.filter(
                template=template,
                grantee=request.user
            ).exists()
        
        except Template.DoesNotExist:
            return False


class HasFormatAccess(permissions.BasePermission):
    """
    Разрешение для доступа к форматам и их настройкам.
    
    Позволяет доступ аутентифицированным пользователям.
    """
    
    def has_permission(self, request, view):
        """Проверка базовых разрешений."""
        # Только аутентифицированные пользователи
        return request.user and request.user.is_authenticated