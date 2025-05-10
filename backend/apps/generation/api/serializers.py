"""
Сериализаторы для приложения генерации документов.
"""
from rest_framework import serializers
from django.utils import timezone

# Правильные импорты
from apps.generation.models import RenderTask, GeneratedDocument
from apps.templates.models import Template, Page, Format, FormatSetting, Unit, PageSettings
from apps.generation.api.validators import TemplateDataValidator


class GenerateDocumentSerializer(serializers.Serializer):
    """
    Сериализатор для запроса генерации документа.
    """
    data = serializers.DictField(required=True, help_text="Данные для подстановки в шаблон")
    
    def validate(self, attrs):
        """Валидирует данные на соответствие шаблону."""
        template = self.context.get('template')
        data = attrs.get('data', {})
        
        if template:
            is_valid, errors = TemplateDataValidator.validate_template_data(template, data)
            if not is_valid:
                raise serializers.ValidationError({
                    'detail': 'Ошибки в данных для шаблона',
                    'errors': errors,
                    'template_fields': self._get_template_fields_structure(template)
                })
        
        return attrs
    
    def _get_template_fields_structure(self, template):
        """Структурирует поля шаблона для ответа на ошибку."""
        global_fields = []
        page_fields = {}
        
        for field in template.fields.all():
            field_data = {
                'key': field.key,
                'label': field.label,
                'required': field.is_required,
                'type': field.type,
            }
            
            if field.default_value:
                field_data['default_value'] = field.default_value
                
            if field.type == 'choices' and field.choices.exists():
                field_data['choices'] = [
                    {'label': choice.label, 'value': choice.value}
                    for choice in field.choices.all()
                ]
            
            if field.page is None:
                global_fields.append(field_data)
            else:
                page_key = str(field.page.index)
                if page_key not in page_fields:
                    page_fields[page_key] = []
                page_fields[page_key].append(field_data)
        
        return {
            'global_fields': global_fields,
            'page_fields': page_fields
        }


class DocumentSerializer(serializers.ModelSerializer):
    """Сериализатор для сгенерированных документов."""
    
    class Meta:
        model = GeneratedDocument
        fields = [
            'id',
            'task',
            'file',
            'content_type',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'task',
            'file',
            'content_type',
            'created_at',
            'updated_at'
        ]


class DocumentDetailSerializer(DocumentSerializer):
    """Детальный сериализатор для документов."""
    task_data = serializers.JSONField(source='task.data_input', read_only=True)
    
    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + ['task_data']


class RenderTaskSerializer(serializers.ModelSerializer):
    """Сериализатор для задач рендеринга."""
    
    class Meta:
        model = RenderTask
        fields = [
            'id',
            'template',
            'version_id',
            'user',
            'request_ip',
            'data_input',
            'status',
            'progress',
            'error',
            'worker_id',
            'created_at',
            'updated_at',
            'finished_at'
        ]
        read_only_fields = [
            'id',
            'version_id',
            'status',
            'progress',
            'error',
            'worker_id',
            'created_at',
            'updated_at',
            'finished_at'
        ]


class RenderTaskDetailSerializer(RenderTaskSerializer):
    """Детальный сериализатор для задач рендеринга."""
    documents = DocumentSerializer(many=True, read_only=True)
    input_data = serializers.JSONField(source='data_input', read_only=True)
    
    class Meta(RenderTaskSerializer.Meta):
        fields = RenderTaskSerializer.Meta.fields + [
            'documents', 'user', 'request_ip', 'input_data', 'worker_id'
        ]
        read_only_fields = fields


# Добавляемые сериализаторы
class UnitSerializer(serializers.ModelSerializer):
    """Сериализатор для единиц измерения."""
    class Meta:
        model = Unit
        fields = ['id', 'key', 'name', 'description']

class FormatSettingSerializer(serializers.ModelSerializer):
    """Сериализатор для настроек формата."""
    class Meta:
        model = FormatSetting
        fields = ['id', 'key', 'name', 'description', 'default_value', 'is_required']

class FormatSerializer(serializers.ModelSerializer):
    """Сериализатор для форматов документов."""
    expected_settings = FormatSettingSerializer(many=True, read_only=True)
    class Meta:
        model = Format
        fields = ['id', 'name', 'description', 'expected_settings', 'render_url']

class PageSettingsSerializer(serializers.ModelSerializer):
    """Сериализатор для настроек страницы шаблона."""
    format_setting = FormatSettingSerializer(read_only=True)
    class Meta:
        model = PageSettings
        fields = ['id', 'format_setting', 'value']

class PageSerializer(serializers.ModelSerializer):
    """Сериализатор для страниц шаблона."""
    settings = PageSettingsSerializer(many=True, read_only=True)
    class Meta:
        model = Page
        fields = ['id', 'index', 'html', 'width', 'height', 'settings']

class TemplateSerializer(serializers.ModelSerializer):
    """Сериализатор для шаблонов документов."""
    pages = PageSerializer(many=True, read_only=True)
    format = FormatSerializer(read_only=True)
    unit = UnitSerializer(read_only=True)
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'description', 'format', 'unit',
            'pages', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class TemplateDataSerializer(serializers.Serializer):
    """Сериализатор для данных шаблона."""
    
    data = serializers.JSONField(validators=[TemplateDataValidator()])
    
    def validate_data(self, value):
        """
        Дополнительная валидация данных шаблона.
        
        Args:
            value: Данные для валидации
            
        Returns:
            dict: Валидированные данные
            
        Raises:
            serializers.ValidationError: При ошибке валидации
        """
        # Здесь можно добавить дополнительную валидацию
        return value