"""
Модели для представления шаблонов документов.
"""
import uuid
from django.db import models
from django.conf import settings
from apps.common.models import BaseModel
from apps.templates.models.unit_format import Unit, Format, FormatSetting


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
    
    class Meta:
        verbose_name = "Шаблон"
        verbose_name_plural = "Шаблоны"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_latest_revision(self):
        """Возвращает последнюю ревизию шаблона."""
        return self.revisions.order_by('-number').first()


class TemplateRevision(BaseModel):
    """
    Ревизия шаблона.
    
    Хранит исторические изменения шаблона, включая HTML и настройки.
    """
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="revisions",
        help_text="Родительский шаблон"
    )
    number = models.PositiveIntegerField(help_text="Номер ревизии (1, 2, …)")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="template_revisions",
        help_text="Кто внёс изменения"
    )
    changelog = models.TextField(blank=True, help_text="Описание изменений")
    html = models.TextField(help_text="Замороженный HTML этой версии")
    
    class Meta:
        verbose_name = "Ревизия шаблона"
        verbose_name_plural = "Ревизии шаблонов"
        ordering = ['-number']
        unique_together = ['template', 'number']
    
    def __str__(self):
        return f"{self.template.name} - v{self.number}"


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


class Field(BaseModel):
    """
    Поле шаблона для ввода данных.
    
    Может быть глобальным (для всего шаблона) или локальным (для страницы).
    """
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="fields",
        help_text="Шаблон"
    )
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="fields",
        help_text="NULL → глобальное поле"
    )
    key = models.CharField(
        max_length=100, 
        help_text="Тех. имя для вставки"
    )
    label = models.CharField(
        max_length=255, 
        help_text="Подпись в UI"
    )
    is_required = models.BooleanField(
        default=False, 
        help_text="Обязательное? (DEF=False)"
    )
    default_value = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="Значение по умолчанию"
    )
    is_choices = models.BooleanField(
        default=False, 
        help_text="Является списком выбора?"
    )
    choices = models.JSONField(
        null=True, 
        blank=True, 
        help_text="Перечень вариантов в формате [{\"value\": \"...\", \"label\": \"...\"}]"
    )
    
    class Meta:
        verbose_name = "Поле шаблона"
        verbose_name_plural = "Поля шаблонов"
        ordering = ['template', 'key']
        # Ключ должен быть уникальным в рамках шаблона или страницы
        unique_together = [
            ['template', 'page', 'key']
        ]
    
    def __str__(self):
        if self.page:
            return f"{self.template.name} - Страница {self.page.index} - {self.key}"
        return f"{self.template.name} - Глобальное - {self.key}"


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