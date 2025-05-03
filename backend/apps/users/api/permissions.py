"""
Классы разрешений для API пользователей.
"""
from rest_framework import permissions


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Разрешение для пользователей: только сам пользователь или администратор может редактировать.
    
    Позволяет GET, HEAD и OPTIONS всем аутентифицированным пользователям,
    но требует быть самим пользователем или администратором для остальных методов.
    """
    
    def has_permission(self, request, view):
        """Проверка базовых разрешений."""
        # Администраторы имеют полный доступ
        if request.user.is_staff:
            return True
        
        # Создание нового пользователя только для администраторов
        if view.action == 'create':
            return request.user.is_staff
        
        # Для остальных действий - проверка индивидуальных разрешений
        return True
    
    def has_object_permission(self, request, view, obj):
        """Проверка разрешений для конкретного объекта."""
        # Администраторы имеют полный доступ
        if request.user.is_staff:
            return True
        
        # Пользователи могут редактировать только свои профили
        return obj.id == request.user.id