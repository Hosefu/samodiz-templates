"""
Сериализаторы для API генерации документов.
"""
from rest_framework import serializers
# Объединяем импорты моделей
from apps.generation.models import (
    RenderTask,
    GeneratedDocument
)
from apps.templates.models import (
    Template,
    Page,
    PageSettings,
    Format,
    FormatSetting,
    Unit
)
from apps.generation.api.validators import TemplateDataValidator
# from django.utils import timezone # Пока не используется здесь, можно будет добавить если нужно


class GenerateDocumentSerializer(serializers.Serializer):
    """
    Сериализатор для запроса генерации документа.
    
    Принимает пользовательские данные для подстановки в шаблон.
    """
    data = serializers.DictField(required=True, help_text="Данные для подстановки в шаблон")
    
    def _get_template_fields(self, template):
        """Получает структурированный список полей шаблона."""
        fields = []
        for field in template.fields.all():
            field_data = {
                'key': field.key,
                'label': field.label,
                'required': field.is_required,
                'page': field.page.index if field.page else None,
                'is_global': field.page is None,
            }
            
            if field.default_value:
                field_data['default_value'] = field.default_value
                
            if field.type == 'choices' and field.choices.exists():
                field_data['is_choices'] = True
                field_data['choices'] = [
                    {'label': choice.label, 'value': choice.value}
                    for choice in field.choices.all()
                ]
                
            fields.append(field_data)
                
        return fields
    
    def validate(self, attrs):
        """Валидирует данные на соответствие шаблону."""
        template = self.context.get('template')
        data = attrs.get('data', {})
        
        if template:
            is_valid, errors = TemplateDataValidator.validate_template_data(template, data)
            if not is_valid:
                # Структурируем поля
                all_fields = template.fields.all()
                global_fields = []
                page_fields = {}
                
                for field in all_fields:
                    field_data = {
                        'key': field.key,
                        'label': field.label,
                        'required': field.is_required,
                    }
                    
                    if field.default_value:
                        field_data['default_value'] = field.default_value
                        
                    if field.type == 'choices' and field.choices.exists():
                        field_data['is_choices'] = True
                        field_data['choices'] = [
                            {'label': choice.label, 'value': choice.value}
                            for choice in field.choices.all()
                        ]
                    
                    if field.page is None:
                        field_data['is_global'] = True
                        global_fields.append(field_data)
                    else:
                        field_data['is_global'] = False
                        field_data['page'] = field.page.index
                        page_key = str(field.page.index)
                        if page_key not in page_fields:
                            page_fields[page_key] = []
                        page_fields[page_key].append(field_data)
                
                raise serializers.ValidationError({
                    'detail': 'Ошибки в данных для шаблона',
                    'errors': errors,
                    'expected_fields': {
                        'global_fields': global_fields,
                        'page_fields': page_fields
                    }
                })
        
        return attrs


class DocumentSerializer(serializers.ModelSerializer):
    """Сериализатор для сгенерированных документов."""
    
    template_name = serializers.CharField(source='task.template.name', read_only=True)
    format = serializers.CharField(source='task.template.format.name', read_only=True)
    
    class Meta:
        model = GeneratedDocument
        fields = [
            'id', 'task', 'file', 'file_name', 'size_bytes', 
            'content_type', 'template_name', 'format', 'created_at'
        ]
        read_only_fields = fields


class DocumentDetailSerializer(DocumentSerializer):
    """Расширенный сериализатор для детального представления документа."""
    
    task_data = serializers.JSONField(source='task.data_input', read_only=True)
    
    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + ['task_data']


class RenderTaskSerializer(serializers.ModelSerializer):
    """Сериализатор для задач рендеринга."""
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    format = serializers.CharField(source='template.format.name', read_only=True)
    
    class Meta:
        model = RenderTask
        fields = [
            'id', 'template', 'template_name', 'format',
            'status', 'progress', 'error', 'started_at', 'finished_at'
        ]
        read_only_fields = fields


class RenderTaskDetailSerializer(RenderTaskSerializer):
    """Расширенный сериализатор для детального представления задачи рендеринга."""
    
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