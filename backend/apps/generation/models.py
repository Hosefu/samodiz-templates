"""
Модели для задач генерации документов и готовых документов.
"""
from django.db import models
from django.conf import settings
from apps.common.models import BaseModel
from apps.templates.models.template import Template


class RenderTask(BaseModel):
    """
    Задача рендеринга документа.
    
    Хранит информацию о процессе генерации документа на основе шаблона.
    """
    STATUS_CHOICES = (
        ('pending', 'В очереди'),
        ('processing', 'В обработке'),
        ('done', 'Завершено'),
        ('failed', 'Ошибка'),
    )
    
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="render_tasks",
        help_text="Шаблон, на основе которого рендерится документ"
    )
    version_id = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="ID версии шаблона в системе версионирования"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="render_tasks",
        help_text="Кто запросил"
    )
    request_ip = models.GenericIPAddressField(
        help_text="IP клиента"
    )
    data_input = models.JSONField(
        help_text="Сырые данные"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Статус"
    )
    worker_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Celery task id"
    )
    progress = models.IntegerField(
        default=0,
        help_text="% выполнения (0-100)"
    )
    error = models.TextField(
        null=True,
        blank=True,
        help_text="Сообщение об ошибке"
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Когда началось"
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Когда завершилось"
    )
    
    class Meta:
        verbose_name = "Задача рендеринга"
        verbose_name_plural = "Задачи рендеринга"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Задача {self.id} - {self.get_status_display()}"
    
    def get_template_version(self):
        """Получает версию шаблона из django-reversion."""
        if self.version_id:
            try:
                from reversion.models import Version
                return Version.objects.get(id=self.version_id)
            except Version.DoesNotExist:
                return None
        return None


class Document(BaseModel):
    """
    Готовый сгенерированный документ.
    
    Содержит ссылку на файл в Ceph и связан с задачей рендеринга.
    """
    task = models.ForeignKey(
        RenderTask,
        on_delete=models.CASCADE,
        related_name="documents",
        help_text="По какой задаче"
    )
    file = models.CharField(
        max_length=1000,
        help_text="URL файла в Ceph"
    )
    size_bytes = models.BigIntegerField(
        help_text="Размер"
    )
    file_name = models.CharField(
        max_length=255,
        help_text="Имя файла"
    )
    content_type = models.CharField(
        max_length=100,
        help_text="Content-Type"
    )
    
    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Документ {self.file_name} ({self.id})"