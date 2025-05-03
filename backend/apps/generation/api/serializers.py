"""
Сериализаторы для API генерации документов.
"""
from rest_framework import serializers
from apps.generation.models import RenderTask, Document
from apps.templates.api.serializers import TemplateRevisionSerializer


class GenerateDocumentSerializer(serializers.Serializer):
    """
    Сериализатор для запроса генерации документа.
    
    Принимает пользовательские данные для подстановки в шаблон.
    """
    data = serializers.DictField(required=True, help_text="Данные для подстановки в шаблон")


class DocumentSerializer(serializers.ModelSerializer):
    """Сериализатор для сгенерированных документов."""
    
    template_name = serializers.CharField(source='task.template_revision.template.name', read_only=True)
    format = serializers.CharField(source='task.template_revision.template.format.name', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'task', 'file', 'file_name', 'size_bytes', 
            'content_type', 'template_name', 'format', 'created_at'
        ]
        read_only_fields = fields


class DocumentDetailSerializer(DocumentSerializer):
    """Расширенный сериализатор для детального представления документа."""
    
    task_id = serializers.UUIDField(source='task.id', read_only=True)
    created_by = serializers.CharField(source='task.user.get_full_name', read_only=True)
    
    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + ['task_id', 'created_by']
        read_only_fields = fields


class RenderTaskSerializer(serializers.ModelSerializer):
    """Сериализатор для задач рендеринга."""
    
    template_name = serializers.CharField(source='template_revision.template.name', read_only=True)
    format = serializers.CharField(source='template_revision.template.format.name', read_only=True)
    
    class Meta:
        model = RenderTask
        fields = [
            'id', 'template_revision', 'template_name', 'format',
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