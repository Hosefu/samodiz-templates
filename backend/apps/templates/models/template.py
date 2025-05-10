"""
Модели для представления шаблонов документов.
"""
import uuid
from django.db import models
from django.conf import settings
from reversion import register
from apps.common.models import BaseModel
from apps.templates.models.unit_format import Unit, Format, FormatSetting


@register(follow=['pages', 'fields', 'assets'])
class Template(BaseModel):
    """
    Шаблон документа.
    
    Основная сущность системы, содержит настройки и HTML-шаблон для генерации документов.
    """
    name = models.CharField(max_length=255, help_text="Название шаблона")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="templates",
        help_text="Владелец шаблона"
    )
    is_public = models.BooleanField(default=False, help_text="Опубликовано?")
    format = models.ForeignKey(
        Format,
        on_delete=models.PROTECT,
        related_name="templates",
        help_text="Формат шаблона"
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="templates",
        help_text="Единица измерения для шаблона"
    )
    description = models.TextField(blank=True, help_text="Описание шаблона")
    html = models.TextField(blank=True, help_text="HTML-код шаблона")
    
    class Meta:
        verbose_name = "Шаблон"
        verbose_name_plural = "Шаблоны"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


@register()
class Page(BaseModel):
    """
    Страница шаблона.
    
    Каждый шаблон может содержать несколько страниц с разными настройками.
    """
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="pages",
        help_text="Родительский шаблон"
    )
    index = models.PositiveIntegerField(help_text="Порядковый номер (1…)")
    html = models.TextField(help_text="HTML-код страницы")
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Ширина страницы"
    )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Высота страницы"
    )
    
    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"
        ordering = ['template', 'index']
        unique_together = ['template', 'index']
    
    def __str__(self):
        return f"{self.template.name} - Страница {self.index}"


class TemplatePermission(BaseModel):
    """
    Разрешение на доступ к шаблону.
    
    Определяет уровень доступа для пользователей или публичных ссылок.
    """
    ROLE_CHOICES = (
        ('viewer', 'Просмотр'),
        ('editor', 'Редактирование'),
        ('owner', 'Владелец'),
    )
    
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="permissions",
        help_text="Шаблон"
    )
    grantee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="template_permissions",
        help_text="Кому выдано (NULL → публичная ссылка)"
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='viewer',
        help_text="Уровень доступа"
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        null=True,
        blank=True,
        help_text="Публичный токен (если grantee=NULL)"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Срок действия ссылки"
    )
    
    class Meta:
        verbose_name = "Разрешение на шаблон"
        verbose_name_plural = "Разрешения на шаблоны"
        ordering = ['template', 'role']
        # Избегаем дублирования разрешений для одного пользователя
        unique_together = ['template', 'grantee']
    
    def __str__(self):
        if self.grantee:
            return f"{self.template.name} - {self.grantee.username} ({self.role})"
        return f"{self.template.name} - Public ({self.role})"


class PageSettings(BaseModel):
    """
    Настройки страницы для конкретного формата.
    
    Хранит значения настроек форматов для каждой страницы.
    """
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="settings",
        help_text="Страница"
    )
    format_setting = models.ForeignKey(
        FormatSetting,
        on_delete=models.CASCADE,
        related_name="page_settings",
        help_text="Какая настройка"
    )
    value = models.CharField(
        max_length=255,
        help_text="Значение для этой страницы"
    )
    
    class Meta:
        verbose_name = "Настройка страницы"
        verbose_name_plural = "Настройки страниц"
        ordering = ['page', 'format_setting']
        unique_together = ['page', 'format_setting']
    
    def __str__(self):
        return f"{self.page} - {self.format_setting.name}: {self.value}"


@register()
class Field(BaseModel):
    """Поле шаблона для ввода данных."""
    FIELD_TYPES = (
        ('string', 'Строка'),
        ('choices', 'Выбор из списка'),
    )
    
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name="fields")
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True, blank=True, related_name="fields")
    key = models.CharField(max_length=100, help_text="Технический ключ")
    label = models.CharField(max_length=255, help_text="Отображаемое название")
    type = models.CharField(
        max_length=20,
        choices=FIELD_TYPES,
        default='string',
        help_text="Тип поля"
    )
    
    # Позиционирование
    order = models.PositiveIntegerField(help_text="Порядок отображения поля")
    
    # Мета-информация о поле
    is_required = models.BooleanField(default=False)
    default_value = models.TextField(blank=True, null=True)
    placeholder = models.CharField(max_length=255, blank=True)
    help_text = models.TextField(blank=True)
    
    class Meta:
        ordering = ['page', 'order', 'created_at']
        unique_together = [['template', 'page', 'key']]
    
    def save(self, *args, **kwargs):
        # Автоматически назначаем order при создании, если не указан
        if self.pk is None and self.order is None:
            # Находим максимальный order для данного контекста
            filters = {'template': self.template}
            if self.page:
                filters['page'] = self.page
            else:
                filters['page__isnull'] = True
                
            max_order = Field.objects.filter(**filters).aggregate(
                max_order=models.Max('order')
            )['max_order']
            
            self.order = (max_order or 0) + 1
            
        super().save(*args, **kwargs)

    def __str__(self):
        if self.page:
            return f"{self.template.name} - Страница {self.page.index} - {self.key}"
        return f"{self.template.name} - Глобальное - {self.key}"


@register()
class FieldChoice(BaseModel):
    """Варианты выбора для полей типа choices."""
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="choices")
    label = models.CharField(max_length=255, help_text="Отображаемое название")
    value = models.CharField(max_length=255, help_text="Значение для шаблона")
    order = models.PositiveIntegerField(default=0, help_text="Порядок отображения")
    
    class Meta:
        ordering = ['field', 'order', 'created_at']
        unique_together = [['field', 'value'], ['field', 'order']]
    
    def __str__(self):
        return f"{self.field.key} - {self.label}"


@register()
class Asset(BaseModel):
    """
    Ассет шаблона (шрифт, изображение).
    
    Может быть глобальным (для всего шаблона) или локальным (для страницы).
    """
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="assets",
        help_text="Шаблон"
    )
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assets",
        help_text="NULL → глобальный ассет"
    )
    name = models.CharField(max_length=255, help_text="Имя файла")
    file = models.CharField(max_length=1000, help_text="URL в Ceph")
    size_bytes = models.BigIntegerField(help_text="Размер в байтах")
    mime_type = models.CharField(max_length=100, help_text="MIME-тип файла")
    
    class Meta:
        verbose_name = "Ассет"
        verbose_name_plural = "Ассеты"
        ordering = ['template', 'name']
    
    def __str__(self):
        if self.page:
            return f"{self.template.name} - Страница {self.page.index} - {self.name}"
        return f"{self.template.name} - Глобальный - {self.name}"


class FieldVersion(BaseModel):
    """Версии структуры полей шаблона."""
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name="field_versions")
    version_number = models.PositiveIntegerField()
    fields_snapshot = models.JSONField(help_text="Снимок структуры полей")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        unique_together = ['template', 'version_number']
        ordering = ['-version_number']