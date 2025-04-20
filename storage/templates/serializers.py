# storage/templates/serializers.py
from rest_framework import serializers
from .models import Template, Page, Field, PageAsset, GeneratedTemplate, PageSettings

class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ['name', 'label', 'required']

class PageAssetSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    def get_file(self, obj):
        # Return relative path /media/...
        return obj.file.url

    class Meta:
        model = PageAsset
        fields = ['file']

class PageSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageSettings
        fields = ['key', 'value']

class PageSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True, read_only=True)
    assets = PageAssetSerializer(many=True, read_only=True)
    settings = PageSettingsSerializer(many=True, read_only=True)

    class Meta:
        model = Page
        fields = ['name', 'html', 'width', 'height', 'units', 'bleeds', 'assets', 'fields', 'settings']

class TemplateSerializer(serializers.ModelSerializer):
    pages = PageSerializer(many=True, read_only=True)

    class Meta:
        model = Template
        fields = ['id', 'name', 'version', 'type', 'pages']

class GeneratedTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedTemplate
        fields = ['id', 'file', 'format', 'created_at']