from django.contrib import admin
import nested_admin
from .models import Template, Page, Field, PageAsset, GeneratedTemplate, PageSettings

class FieldInline(nested_admin.NestedTabularInline):
    model = Field
    extra = 1

class PageSettingsInline(nested_admin.NestedTabularInline):
    model = PageSettings
    extra = 1

class PageAssetInline(nested_admin.NestedTabularInline):
    model = PageAsset
    extra = 1

class PageInline(nested_admin.NestedTabularInline):
    model = Page
    inlines = [FieldInline, PageAssetInline, PageSettingsInline]
    extra = 1

@admin.register(Template)
class TemplateAdmin(nested_admin.NestedModelAdmin):
    inlines = [PageInline]
    list_display = ['name', 'version', 'type', 'generated_files_count']
    list_filter = ['type']
    
    def generated_files_count(self, obj):
        return obj.generated_templates.count()
    generated_files_count.short_description = 'Generated Files'

@admin.register(GeneratedTemplate)
class GeneratedTemplateAdmin(admin.ModelAdmin):
    list_display = ['template', 'format', 'created_at', 'file_link']
    list_filter = ['template', 'format', 'created_at']
    search_fields = ['template__name', 'data']
    readonly_fields = ['template', 'format', 'created_at', 'file_link']
    
    def file_link(self, obj):
        return f'<a href="{obj.file.url}" target="_blank">{obj.file.name.split("/")[-1]}</a>'
    file_link.short_description = 'File'
    file_link.allow_tags = True