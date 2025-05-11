"""
Сериализаторы для API шаблонов.
"""
from rest_framework import serializers
from apps.templates.models.unit_format import Unit, Format, FormatSetting
from apps.templates.models.template import (
    Template, TemplatePermission, Page, PageSettings, Field, Asset, FieldChoice
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


class FieldChoiceSerializer(serializers.ModelSerializer):
    """Сериализатор для вариантов выбора поля."""
    
    class Meta:
        model = FieldChoice
        fields = ['id', 'label', 'value', 'order']
        read_only_fields = ['id']


class FieldSerializer(serializers.ModelSerializer):
    """Сериализатор для полей шаблона."""
    
    choices = FieldChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Field
        fields = [
            'id', 'page', 'key', 'label', 'type', 'is_required', 
            'default_value', 'placeholder', 'help_text', 'choices'
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
        
        # Включаем choices только для полей типа choices
        if instance.type != 'choices':
            data.pop('choices', None)
        
        return data


class AssetSerializer(serializers.ModelSerializer):
    """Сериализатор для ресурсов шаблона."""
    
    class Meta:
        model = Asset
        fields = ['id', 'page', 'name', 'file', 'mime_type']
        read_only_fields = ['id']


class PageSerializer(serializers.ModelSerializer):
    """Сериализатор для страниц шаблона."""
    
    settings = PageSettingsSerializer(many=True, read_only=True)
    fields = FieldSerializer(many=True, read_only=True)
    assets = AssetSerializer(many=True, read_only=True)
    
    class Meta:
        model = Page
        fields = [
            'id', 'template', 'index', 'width', 'height',
            'settings', 'fields', 'assets', 'html'
        ]
        read_only_fields = ['id']
    
    def to_representation(self, instance):
        """Кастомизируем вывод, исключая HTML для неавторизованных пользователей."""
        data = super().to_representation(instance)
        
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            # Удаляем поле html из ответа
            data.pop('html', None)
            return data
        
        template = instance.template
        if not (request.user == template.owner or 
                template.permissions.filter(grantee=request.user, role__in=['editor', 'owner']).exists()):
            # Удаляем поле html из ответа
            data.pop('html', None)
        
        return data


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
    
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    pages_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'description', 'is_public', 
            'owner', 'owner_name', 'pages_count'
        ]
        read_only_fields = ['id', 'owner', 'owner_name', 'pages_count']
    
    def get_pages_count(self, obj):
        return obj.pages.count()


class TemplateDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации о шаблоне."""
    
    pages = PageSerializer(many=True, read_only=True)
    global_fields = serializers.SerializerMethodField()
    global_assets = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'description', 'is_public', 
            'format', 'unit', 'pages', 'global_fields',
            'permissions', 'global_assets'
        ]
        read_only_fields = ['id']
    
    def get_global_fields(self, obj):
        """Получает глобальные поля шаблона."""
        fields = obj.fields.filter(page__isnull=True)
        return FieldSerializer(fields, many=True).data
    
    def get_global_assets(self, obj):
        """Получает глобальные ассеты шаблона."""
        assets = obj.assets.filter(page__isnull=True)
        return AssetSerializer(assets, many=True).data
    
    def get_permissions(self, obj):
        """Получает разрешения для текущего пользователя."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return {'role': 'anonymous'}
        
        if request.user == obj.owner:
            return {'role': 'owner'}
        
        permission = obj.permissions.filter(grantee=request.user).first()
        if permission:
            return {'role': permission.role}
        
        return {'role': 'viewer' if obj.is_public else 'none'}


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