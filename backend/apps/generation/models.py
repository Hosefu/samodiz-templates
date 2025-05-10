"""
Модели для приложения генерации документов.
"""
import logging
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.templates.models import Template, Format, FormatSetting, Unit, Page
from apps.common.models import BaseModel

logger = logging.getLogger(__name__)


class RenderTask(BaseModel):
    """
    Задачи рендеринга документов.
    
    Отслеживает процесс генерации документа из шаблона.
    """
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('processing', 'В обработке'),
        ('done', 'Завершено'),
        ('failed', 'Ошибка'),
    ]
    
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name='render_tasks',
        help_text="Шаблон"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Статус задачи"
    )
    progress = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        help_text="Прогресс выполнения (0-100)"
    )
    error = models.TextField(blank=True, help_text="Сообщение об ошибке")
    started_at = models.DateTimeField(auto_now_add=True, help_text="Время начала")
    finished_at = models.DateTimeField(null=True, blank=True, help_text="Время завершения")
    
    class Meta:
        verbose_name = "Задача рендеринга"
        verbose_name_plural = "Задачи рендеринга"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.template.name} - {self.get_status_display()}"
    
    def mark_as_done(self):
        """Отмечает задачу как выполненную."""
        self.status = 'done'
        self.progress = 100
        self.finished_at = timezone.now()
        self.save(update_fields=['status', 'progress', 'finished_at'])
    
    def mark_as_failed(self, error_message):
        """Отмечает задачу как завершившуюся с ошибкой."""
        self.status = 'failed'
        self.error = error_message
        self.finished_at = timezone.now()
        self.save(update_fields=['status', 'error', 'finished_at'])


class GeneratedDocument(BaseModel):
    """
    Сгенерированные документы.
    
    Содержит информацию о сгенерированных документах и ссылки на файлы.
    """
    task = models.ForeignKey(
        RenderTask,
        on_delete=models.CASCADE,
        related_name='documents',
        help_text="Задача рендеринга"
    )
    file = models.URLField(help_text="URL файла в хранилище")
    size_bytes = models.PositiveIntegerField(help_text="Размер файла в байтах")
    file_name = models.CharField(max_length=255, help_text="Имя файла")
    content_type = models.CharField(max_length=100, help_text="MIME-тип файла")
    
    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.file_name