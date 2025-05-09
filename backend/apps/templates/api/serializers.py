"""
Сериализаторы для API шаблонов.
"""
from rest_framework import serializers
from apps.templates.models.unit_format import Unit, Format, FormatSetting
from apps.templates.models.template import (
    Template, TemplatePermission, Page, PageSettings, Field, Asset
)
from apps.templates.services.templating import template_renderer


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
            'id', 'page', 'name', 'type', 'required',
            'description', 'default_value', 'choices'
        ]
        read_only_fields = ['id']


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
    
    class Meta:
        model = Page
        fields = [
            'id', 'template', 'index', 'width', 'height',
            'settings', 'fields', 'assets'
        ]
        read_only_fields = ['id']


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
    
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'owner', 'owner_name', 'is_public',
            'format', 'format_name', 'description', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TemplateDetailSerializer(TemplateListSerializer):
    """Расширенный сериализатор для детального представления шаблона."""
    
    pages = PageSerializer(many=True, read_only=True)
    permissions = TemplatePermissionSerializer(many=True, read_only=True)
    
    class Meta(TemplateListSerializer.Meta):
        fields = TemplateListSerializer.Meta.fields + ['html', 'pages', 'permissions']


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