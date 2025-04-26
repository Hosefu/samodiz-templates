from rest_framework import permissions

class IsOwnerOrHasPermission(permissions.BasePermission):
    """
    Пользователь должен быть владельцем или иметь соответствующее разрешение
    """
    def has_object_permission(self, request, view, obj):
        # Админы имеют доступ ко всему
        if request.user.is_admin():
            return True
            
        # Проверяем, владелец ли текущий пользователь
        if obj.owner == request.user:
            return True
            
        # Проверяем публичный доступ
        if obj.is_public and request.method in permissions.SAFE_METHODS:
            return True
            
        # Получаем необходимое разрешение
        required_permission = 'view' if request.method in permissions.SAFE_METHODS else 'edit'
        
        # Проверяем прямые права пользователя
        user_permission = obj.permissions.filter(
            user=request.user,
            permission_type=required_permission
        ).exists()
        
        if user_permission:
            return True
            
        # Проверяем групповые права
        user_groups = request.user.custom_groups.all()
        group_permission = obj.permissions.filter(
            group__in=user_groups,
            permission_type=required_permission
        ).exists()
        
        return group_permission

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает доступ на чтение всем, а на запись только администраторам
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_admin() 