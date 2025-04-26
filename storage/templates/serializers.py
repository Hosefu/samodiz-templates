# storage/templates/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Template, TemplatePermission, UserGroup, Page, Field, PageAsset, GeneratedTemplate, PageSettings

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_admin']
        read_only_fields = ['id', 'username', 'role', 'is_admin']

class UserGroupSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserGroup
        fields = ['id', 'name', 'description', 'members_count']
    
    def get_members_count(self, obj):
        return obj.members.count()

class TemplatePermissionSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    group_details = UserGroupSerializer(source='group', read_only=True)
    
    class Meta:
        model = TemplatePermission
        fields = ['id', 'template', 'user', 'group', 'permission_type', 'created_at',
                  'user_details', 'group_details']

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
        fields = ['id', 'file']

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
        fields = ['id', 'name', 'html', 'width', 'height', 'units', 'bleeds', 'assets', 'fields', 'settings']

class TemplateSerializer(serializers.ModelSerializer):
    pages = PageSerializer(many=True, read_only=True)

    class Meta:
        model = Template
        fields = ['id', 'name', 'version', 'type', 'pages']

class GeneratedTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedTemplate
        fields = ['id', 'file', 'format', 'created_at']