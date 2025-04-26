from django.contrib import admin
import nested_admin
from django.contrib.auth.admin import UserAdmin
from .models import Template, Page, Field, PageAsset, GeneratedTemplate, PageSettings, User, UserGroup, TemplatePermission

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

# Регистрируем пользовательскую модель
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'date_joined']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Advanced options', {'fields': ('additional_info', 'preferences'), 'classes': ('collapse',)}),
    )
    search_fields = ['username', 'email', 'first_name', 'last_name']

# Регистрируем группы пользователей
@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'member_count']
    search_fields = ['name', 'description']
    filter_horizontal = ['members']
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'

# Модифицируем администрирование разрешений
class TemplatePermissionInline(admin.TabularInline):
    model = TemplatePermission
    extra = 1
    fk_name = 'template'

# Обновляем администрирование шаблонов
@admin.register(Template)
class TemplateAdmin(nested_admin.NestedModelAdmin):
    list_display = ['label', 'name', 'version', 'type', 'owner', 'is_public', 'created_at']
    list_filter = ['type', 'is_public', 'created_at']
    search_fields = ['label', 'name']
    inlines = [PageInline, TemplatePermissionInline]
    
    def generated_files_count(self, obj):
        return obj.generated_templates.count()
    generated_files_count.short_description = 'Generated Files'

# Регистрируем модель разрешений
@admin.register(TemplatePermission)
class TemplatePermissionAdmin(admin.ModelAdmin):
    list_display = ['template', 'get_user_or_group', 'permission_type', 'created_at']
    list_filter = ['permission_type', 'created_at']
    search_fields = ['template__name', 'template__label', 'user__username', 'group__name']
    
    def get_user_or_group(self, obj):
        if obj.user:
            return f"User: {obj.user.username}"
        elif obj.group:
            return f"Group: {obj.group.name}"
        return "None"
    get_user_or_group.short_description = 'Granted to'

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