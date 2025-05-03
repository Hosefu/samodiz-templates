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


class FormatSettingSerializer(serializers.ModelSerializer):
    """Сериализатор для настроек формата."""
    
    class Meta:
        model = FormatSetting
        fields = ['id', 'name', 'description', 'key', 'is_required', 'default_value']
        read_only_fields = ['id']


class FormatSerializer(serializers.ModelSerializer):
    """Сериализатор для форматов документов."""
    
    expected_settings = FormatSettingSerializer(many=True, read_only=True)
    allowed_units = UnitSerializer(many=True, read_only=True)
    
    class Meta:
        model = Format
        fields = ['id', 'name', 'description', 'expected_settings', 'allowed_units']
        read_only_fields = ['id']


class FormatDetailSerializer(FormatSerializer):
    """Расширенный сериализатор для детального представления формата."""
    
    class Meta(FormatSerializer.Meta):
        fields = FormatSerializer.Meta.fields + ['render_url']


class FieldSerializer(serializers.ModelSerializer):
    """Сериализатор для полей шаблона."""
    
    class Meta:
        model = Field
        fields = [
            'id', 'template', 'page', 'key', 'label', 
            'is_required', 'default_value', 'is_choices', 'choices'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """Проверяет корректность данных."""
        # Проверяем, что поле с выбором содержит корректный формат
        if data.get('is_choices') and not data.get('choices'):
            raise serializers.ValidationError(
                {'choices': 'Для поля с выбором необходимо указать варианты.'}
            )
        
        # Проверяем формат choices
        if data.get('choices'):
            if not isinstance(data['choices'], list):
                raise serializers.ValidationError(
                    {'choices': 'Варианты должны быть представлены в виде списка.'}
                )
            
            for choice in data['choices']:
                if not isinstance(choice, dict) or 'value' not in choice or 'label' not in choice:
                    raise serializers.ValidationError(
                        {'choices': 'Каждый вариант должен иметь поля "value" и "label".'}
                    )
        
        return data


class AssetSerializer(serializers.ModelSerializer):
    """Сериализатор для ассетов шаблона."""
    
    class Meta:
        model = Asset
        fields = ['id', 'template', 'page', 'name', 'file', 'size_bytes', 'mime_type']
        read_only_fields = ['id', 'size_bytes', 'mime_type']


class PageSettingsSerializer(serializers.ModelSerializer):
    """Сериализатор для настроек страницы."""
    
    format_setting_name = serializers.CharField(source='format_setting.name', read_only=True)
    
    class Meta:
        model = PageSettings
        fields = ['id', 'format_setting', 'format_setting_name', 'value']
        read_only_fields = ['id', 'format_setting_name']


class PageSerializer(serializers.ModelSerializer):
    """Сериализатор для страниц шаблона."""
    
    settings = PageSettingsSerializer(many=True, read_only=True)
    fields = FieldSerializer(many=True, read_only=True)
    assets = AssetSerializer(many=True, read_only=True)
    
    class Meta:
        model = Page
        fields = ['id', 'template', 'index', 'html', 'width', 'height', 'settings', 'fields', 'assets']
        read_only_fields = ['id']
    
    def validate_html(self, value):
        """Проверяет синтаксис HTML шаблона."""
        errors = template_renderer.validate_template(value)
        if errors:
            error_messages = [f"Строка {e['line']}: {e['message']}" for e in errors]
            raise serializers.ValidationError(error_messages)
        return value


class TemplateListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка шаблонов."""
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    format_name = serializers.CharField(source='format.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'owner', 'owner_name', 'is_public',
            'format', 'format_name', 'unit', 'unit_name',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TemplateDetailSerializer(TemplateListSerializer):
    """Расширенный сериализатор для детального представления шаблона."""
    
    pages = PageSerializer(many=True, read_only=True)
    global_fields = serializers.SerializerMethodField()
    global_assets = serializers.SerializerMethodField()
    
    class Meta(TemplateListSerializer.Meta):
        fields = TemplateListSerializer.Meta.fields + ['pages', 'global_fields', 'global_assets']
    
    def get_global_fields(self, obj):
        """Возвращает глобальные поля шаблона."""
        fields = obj.fields.filter(page__isnull=True)
        return FieldSerializer(fields, many=True).data
    
    def get_global_assets(self, obj):
        """Возвращает глобальные ассеты шаблона."""
        assets = obj.assets.filter(page__isnull=True)
        return AssetSerializer(assets, many=True).data


class TemplateCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания шаблона."""
    
    class Meta:
        model = Template
        fields = ['id', 'name', 'format', 'unit', 'description', 'is_public']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        """Создает шаблон с привязкой к текущему пользователю."""
        request = self.context.get('request')
        validated_data['owner'] = request.user
        return super().create(validated_data)


class TemplateVersionSerializer(serializers.Serializer):
    """Сериализатор для версий шаблона."""
    id = serializers.IntegerField()
    revision_id = serializers.IntegerField()
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