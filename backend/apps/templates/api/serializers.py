"""
Сериализаторы для API шаблонов.
"""
from rest_framework import serializers
from apps.templates.models.unit_format import Unit, Format, FormatSetting
from apps.templates.models.template import (
    Template, TemplatePermission, Page, PageSettings, Field, Asset
)
from apps.templates.services.templating import template_renderer
from django.db.models import Q


class UnitSerializer(serializers.ModelSerializer):
    """Сериализатор для единиц измерения."""
    
    class Meta:
        model = Unit
        fields = ['id', 'key', 'name']
        read_only_fields = ['id']


class FormatSerializer(serializers.ModelSerializer):
    """Сериализатор для форматов."""
    
    class Meta:
        model = Format
        fields = ['id', 'name', 'key', 'description']
        read_only_fields = ['id']


class FormatSettingSerializer(serializers.ModelSerializer):
    """Сериализатор для настроек формата."""
    
    class Meta:
        model = FormatSetting
        fields = ['id', 'key', 'name', 'type', 'default_value', 'description']
        read_only_fields = ['id']


class FormatDetailSerializer(FormatSerializer):
    """Расширенный сериализатор для формата с настройками."""
    
    settings = FormatSettingSerializer(many=True, read_only=True)
    
    class Meta(FormatSerializer.Meta):
        fields = FormatSerializer.Meta.fields + ['settings']


class PageSettingsSerializer(serializers.ModelSerializer):
    """Сериализатор для настроек страницы."""
    
    class Meta:
        model = PageSettings
        fields = ['id', 'page', 'format_setting', 'value']
        read_only_fields = ['id']


class FieldSerializer(serializers.ModelSerializer):
    """Сериализатор для полей шаблона."""
    
    class Meta:
        model = Field
        fields = [
            'id', 'page', 'key', 'label', 'is_required', 
            'default_value', 'is_choices', 'choices'
        ]
        read_only_fields = ['id']

    def to_representation(self, instance):
        """Настраиваем представление поля."""
        data = super().to_representation(instance)
        
        # Переименовываем is_required в required для API
        data['required'] = data.pop('is_required', False)
        
        # Добавляем номер страницы только если поле привязано к странице
        if instance.page:
            data['page_number'] = instance.page.index
        
        # Убираем избыточные поля для страничных полей
        # так как они уже находятся внутри структуры страницы
        return data


class AssetSerializer(serializers.ModelSerializer):
    """Сериализатор для ресурсов шаблона."""
    
    class Meta:
        model = Asset
        fields = ['id', 'page', 'name', 'file', 'content_type']
        read_only_fields = ['id']


class PageSerializer(serializers.ModelSerializer):
    """Сериализатор для страниц шаблона."""
    
    settings = PageSettingsSerializer(many=True, read_only=True)
    fields = FieldSerializer(many=True, read_only=True)
    assets = AssetSerializer(many=True, read_only=True)
    html = serializers.SerializerMethodField()
    
    class Meta:
        model = Page
        fields = [
            'id', 'template', 'index', 'width', 'height',
            'settings', 'fields', 'assets', 'html'
        ]
        read_only_fields = ['id']
    
    def get_html(self, obj):
        """Возвращает HTML только для владельца или редактора."""
        request = self.context.get('request')
        
        if not request or not request.user or not request.user.is_authenticated:
            return None
        
        # Владелец или администратор всегда получает HTML
        if obj.template.owner == request.user or request.user.is_staff:
            return obj.html
        
        # Проверяем права редактора (только editor или owner)
        permission = TemplatePermission.objects.filter(
            template=obj.template,
            grantee=request.user,
            role__in=['editor', 'owner']
        ).exists()
        
        if permission:
            return obj.html
        
        # Для всех остальных (включая viewer) HTML не показываем
        return None


class TemplatePermissionSerializer(serializers.ModelSerializer):
    """Сериализатор для разрешений на шаблон."""
    
    grantee_name = serializers.CharField(source='grantee.get_full_name', read_only=True)
    
    class Meta:
        model = TemplatePermission
        fields = [
            'id', 'template', 'grantee', 'grantee_name',
            'role', 'token', 'expires_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TemplateListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка шаблонов."""
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    format_name = serializers.CharField(source='format.name', read_only=True)
    pages_count = serializers.IntegerField(source='pages.count', read_only=True)
    
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'owner', 'owner_name', 'is_public',
            'format', 'format_name', 'description', 'pages_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TemplateDetailSerializer(serializers.ModelSerializer):
    """Расширенный сериализатор для детального представления шаблона."""
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    format_name = serializers.CharField(source='format.name', read_only=True)
    pages = serializers.SerializerMethodField()
    global_fields = serializers.SerializerMethodField()
    global_assets = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    html = serializers.SerializerMethodField()
    
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'owner', 'owner_name', 'is_public',
            'format', 'format_name', 'description', 'created_at',
            'html', 'pages', 'global_fields', 'global_assets', 'permissions'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_html(self, obj):
        """Возвращает HTML только для владельца или редактора."""
        request = self.context.get('request')
        
        if not request or not request.user or not request.user.is_authenticated:
            return None
        
        # Владелец или администратор всегда получает HTML
        if obj.owner == request.user or request.user.is_staff:
            return obj.html
        
        # Проверяем права редактора (только editor или owner)
        permission = TemplatePermission.objects.filter(
            template=obj,
            grantee=request.user,
            role__in=['editor', 'owner']
        ).exists()
        
        if permission:
            return obj.html
        
        # Для всех остальных (включая viewer) HTML не показываем
        return None
    
    def get_pages(self, obj):
        """Возвращает страницы с их полями и ассетами."""
        pages = obj.pages.all().order_by('index')
        return PageSerializer(pages, many=True, context=self.context).data
    
    def get_global_fields(self, obj):
        """Возвращает только глобальные поля шаблона."""
        global_fields = obj.fields.filter(page__isnull=True)
        serializer = FieldSerializer(global_fields, many=True)
        return serializer.data
    
    def get_global_assets(self, obj):
        """Возвращает только глобальные ассеты шаблона."""
        global_assets = obj.assets.filter(page__isnull=True)
        serializer = AssetSerializer(global_assets, many=True)
        return serializer.data
    
    def get_permissions(self, obj):
        """Возвращает разрешения с учетом прав текущего пользователя."""
        request = self.context.get('request')
        permissions = obj.permissions.all()
        
        # Владелец и админ видят все разрешения
        if request and request.user and request.user.is_authenticated:
            if obj.owner == request.user or request.user.is_staff:
                return TemplatePermissionSerializer(permissions, many=True).data
        
        # Остальные видят только публичные разрешения и свои
        if request and request.user and request.user.is_authenticated:
            permissions = permissions.filter(
                Q(grantee=request.user) | Q(grantee__isnull=True)
            )
        else:
            permissions = permissions.filter(grantee__isnull=True)
        
        return TemplatePermissionSerializer(permissions, many=True).data


class TemplateCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания шаблона."""
    
    class Meta:
        model = Template
        fields = [
            'name', 'format', 'unit', 'description', 'html',
            'is_public'
        ]


class VersionSerializer(serializers.Serializer):
    """Сериализатор для версий шаблона из django-reversion."""
    
    id = serializers.IntegerField()
    date_created = serializers.DateTimeField()
    user = serializers.SerializerMethodField()
    comment = serializers.CharField()
    
    def get_user(self, obj):
        """Получает информацию о пользователе."""
        user_data = obj.get('user', {})
        return {
            'id': user_data.get('id'),
            'email': user_data.get('email'),
            'full_name': user_data.get('full_name')
        }


class TemplateVersionSerializer(serializers.Serializer):
    """Сериализатор для версий шаблона из django-reversion."""
    id = serializers.IntegerField()
    date_created = serializers.DateTimeField(source='revision.date_created')
    user = serializers.SerializerMethodField()
    comment = serializers.CharField(source='revision.comment')
    
    def get_user(self, obj):
        user = obj.revision.user
        if user:
            return {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.get_full_name()
            }
        return None