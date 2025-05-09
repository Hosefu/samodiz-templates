"""
Сериализаторы для API генерации документов.
"""
from rest_framework import serializers
from apps.generation.models import RenderTask, Document
from apps.generation.api.validators import TemplateDataValidator


class GenerateDocumentSerializer(serializers.Serializer):
    """
    Сериализатор для запроса генерации документа.
    
    Принимает пользовательские данные для подстановки в шаблон.
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
                    'expected_fields': self._get_template_fields(template)
                })
        
        return attrs
    
    def _get_template_fields(self, template):
        """Получает список полей шаблона для валидации."""
        fields = []
        for page in template.pages.all():
            for field in page.fields.all():
                fields.append({
                    'name': field.name,
                    'type': field.type,
                    'required': field.required,
                    'description': field.description
                })
        return fields


class DocumentSerializer(serializers.ModelSerializer):
    """Сериализатор для сгенерированных документов."""
    
    template_name = serializers.CharField(source='task.template.name', read_only=True)
    format = serializers.CharField(source='task.template.format.name', read_only=True)
    
    class Meta:
        model = Document
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