from rest_framework import serializers
from .models import Template, Page, Field, PageAsset

class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ['name', 'label', 'required']

class PageAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageAsset
        fields = ['file']

class PageSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True, read_only=True)
    assets = PageAssetSerializer(many=True, read_only=True)

    class Meta:
        model = Page
        fields = ['name', 'html', 'width', 'height', 'bleeds', 'assets', 'fields']

class TemplateSerializer(serializers.ModelSerializer):
    pages = PageSerializer(many=True, read_only=True)

    class Meta:
        model = Template
        fields = ['id', 'name', 'version', 'pages']  # Убрали 'assets'