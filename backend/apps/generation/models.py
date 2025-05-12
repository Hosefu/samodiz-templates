"""
Модели для приложения генерации документов.
"""
import logging
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.templates.models import Template
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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='render_tasks',
        help_text="Пользователь, запросивший рендеринг"
    )
    
    # Ссылка на версию шаблона через reversion
    version_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID версии шаблона из django-reversion"
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
    
    # Данные для рендеринга
    data_input = models.JSONField(
        default=dict,
        help_text="Данные для подстановки в шаблон"
    )
    
    # Информация о запросе
    request_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP адрес запроса"
    )
    worker_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="ID задачи Celery"
    )
    
    # Временные метки
    started_at = models.DateTimeField(auto_now_add=True, help_text="Время начала")
    finished_at = models.DateTimeField(null=True, blank=True, help_text="Время завершения")
    
    # Токен для доступа к документу анонимными пользователями
    document_token = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        help_text="Токен для доступа к документу"
    )
    
    # Время истечения токена
    document_token_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Время истечения токена доступа"
    )
    
    class Meta:
        verbose_name = "Задача рендеринга"
        verbose_name_plural = "Задачи рендеринга"
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['status', '-started_at']),
            models.Index(fields=['user', '-started_at']),
        ]
    
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
    
    def mark_as_processing(self):
        """Отмечает задачу как обрабатываемую."""
        self.status = 'processing'
        self.save(update_fields=['status'])
    
    def update_progress(self, progress):
        """Обновляет прогресс выполнения задачи."""
        self.progress = min(max(progress, 0), 100)
        self.save(update_fields=['progress'])
        
    def generate_document_token(self, expires_in_hours=24):
        """Генерирует токен доступа к документу."""
        import secrets
        from datetime import timedelta
        
        self.document_token = secrets.token_urlsafe(32)
        self.document_token_expires_at = timezone.now() + timedelta(hours=expires_in_hours)
        self.save(update_fields=['document_token', 'document_token_expires_at'])
        
        return self.document_token


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
        indexes = [
            models.Index(fields=['task', '-created_at']),
        ]
    
    def __str__(self):
        return self.file_name