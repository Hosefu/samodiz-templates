"""
Модели для представления форматов документов и единиц измерения.
"""
from django.db import models
from apps.common.models import BaseModel


class Unit(BaseModel):
    """
    Единица измерения (например мм, пиксели).
    
    Используется для указания размеров и позиций в шаблонах.
    """
    key = models.CharField(max_length=10, unique=True, help_text="Значение единицы измерения (например `mm`, `px`)")
    name = models.CharField(max_length=50, help_text="Подпись в UI (`мм`)")
    
    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"
        ordering = ['key']
    
    def __str__(self):
        return f"{self.name} ({self.key})"


class Format(BaseModel):
    """
    Формат документа (PDF, PNG).
    
    Определяет способ рендеринга и настройки для шаблонов.
    """
    name = models.CharField(max_length=50, unique=True, help_text="Название формата (`pdf`, `png`)")
    description = models.TextField(blank=True, help_text="Описание формата")
    render_url = models.URLField(help_text="Внутренний URL генератора")
    allowed_units = models.ManyToManyField(
        Unit, 
        related_name="formats",
        help_text="Разрешённые единицы измерения"
    )
    
    class Meta:
        verbose_name = "Формат"
        verbose_name_plural = "Форматы"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class FormatSetting(BaseModel):
    """
    Настройка для формата.
    
    Определяет параметры рендеринга, специфичные для формата.
    """
    format = models.ForeignKey(
        Format, 
        on_delete=models.CASCADE, 
        related_name="expected_settings",
        help_text="Для какого формата"
    )
    name = models.CharField(max_length=100, help_text="Название настройки")
    description = models.TextField(blank=True, help_text="Описание")
    key = models.CharField(max_length=50, help_text="Ключ")
    is_required = models.BooleanField(default=False, help_text="Обязательна?")
    default_value = models.CharField(max_length=255, blank=True, null=True, help_text="Значение по умолчанию")
    
    class Meta:
        verbose_name = "Настройка формата"
        verbose_name_plural = "Настройки форматов"
        ordering = ['format', 'name']
        # Уникальный ключ для каждого формата
        unique_together = ['format', 'key']
    
    def __str__(self):
        return f"{self.format.name} - {self.name}"