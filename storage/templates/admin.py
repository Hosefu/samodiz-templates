from django.contrib import admin
import nested_admin
from .models import Template, Page, Field, PageAsset

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