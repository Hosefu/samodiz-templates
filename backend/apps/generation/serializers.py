"""
Сериализаторы для приложения генерации документов.
"""
from rest_framework import serializers
from django.utils import timezone

from apps.generation.models import (
    Template,
    TemplatePage,
    TemplatePageSetting,
    RenderTask,
    Document,
    Format,
    FormatSetting,
    Unit
)


class UnitSerializer(serializers.ModelSerializer):
    """Сериализатор для единиц измерения."""
    
    class Meta:
        model = Unit
        fields = ['id', 'key', 'name', 'description']


class FormatSettingSerializer(serializers.ModelSerializer):
    """Сериализатор для настроек формата."""
    
    class Meta:
        model = FormatSetting
        fields = ['id', 'key', 'name', 'description', 'type', 'default_value']


class FormatSerializer(serializers.ModelSerializer):
    """Сериализатор для форматов документов."""
    settings = FormatSettingSerializer(many=True, read_only=True)
    
    class Meta:
        model = Format
        fields = ['id', 'name', 'key', 'description', 'settings', 'renderer_url']


class TemplatePageSettingSerializer(serializers.ModelSerializer):
    """Сериализатор для настроек страницы шаблона."""
    format_setting = FormatSettingSerializer(read_only=True)
    
    class Meta:
        model = TemplatePageSetting
        fields = ['id', 'format_setting', 'value']


class TemplatePageSerializer(serializers.ModelSerializer):
    """Сериализатор для страниц шаблона."""
    settings = TemplatePageSettingSerializer(many=True, read_only=True)
    
    class Meta:
        model = TemplatePage
        fields = ['id', 'index', 'html', 'width', 'height', 'settings']


class TemplateSerializer(serializers.ModelSerializer):
    """Сериализатор для шаблонов документов."""
    pages = TemplatePageSerializer(many=True, read_only=True)
    format = FormatSerializer(read_only=True)
    unit = UnitSerializer(read_only=True)
    
    class Meta:
        model = Template
        fields = [
            'id',
            'name',
            'description',
            'format',
            'unit',
            'pages',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DocumentSerializer(serializers.ModelSerializer):
    """Сериализатор для сгенерированных документов."""
    
    class Meta:
        model = Document
        fields = [
            'id',
            'task',
            'file',
            'size_bytes',
            'file_name',
            'content_type',
            'created_at'
        ]
        read_only_fields = ['created_at']


class RenderTaskSerializer(serializers.ModelSerializer):
    """Сериализатор для задач рендеринга."""
    documents = DocumentSerializer(many=True, read_only=True)
    template = TemplateSerializer(read_only=True)
    
    class Meta:
        model = RenderTask
        fields = [
            'id',
            'template',
            'status',
            'progress',
            'error',
            'documents',
            'started_at',
            'finished_at'
        ]
        read_only_fields = ['started_at', 'finished_at']


class GenerateDocumentSerializer(serializers.Serializer):
    """
    Сериализатор для запроса генерации документа.
    
    Валидирует входные данные для генерации документа из шаблона.
    """
    format = serializers.ChoiceField(
        choices=['pdf', 'png', 'svg'],
        required=True,
        help_text="Формат генерируемого документа"
    )
    data = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Данные для подстановки в шаблон"
    ) 