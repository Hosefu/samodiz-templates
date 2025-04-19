from django.contrib import admin
import nested_admin
from .models import Template, Page, Field, PageAsset, GeneratedPdf

class FieldInline(nested_admin.NestedTabularInline):
    model = Field
    extra = 1

class PageAssetInline(nested_admin.NestedTabularInline):
    model = PageAsset
    extra = 1

class PageInline(nested_admin.NestedTabularInline):
    model = Page
    inlines = [FieldInline, PageAssetInline]
    extra = 1

@admin.register(Template)
class TemplateAdmin(nested_admin.NestedModelAdmin):
    inlines = [PageInline]
    list_display = ['name', 'version', 'generated_pdf_count']
    
    def generated_pdf_count(self, obj):
        return obj.generated_pdfs.count()
    generated_pdf_count.short_description = 'Generated PDFs'

@admin.register(GeneratedPdf)
class GeneratedPdfAdmin(admin.ModelAdmin):
    list_display = ['template', 'created_at', 'file_link']
    list_filter = ['template', 'created_at']
    search_fields = ['template__name', 'data']
    readonly_fields = ['template', 'created_at', 'file_link']
    
    def file_link(self, obj):
        return f'<a href="{obj.file.url}" target="_blank">{obj.file.name.split("/")[-1]}</a>'
    file_link.short_description = 'PDF File'
    file_link.allow_tags = True