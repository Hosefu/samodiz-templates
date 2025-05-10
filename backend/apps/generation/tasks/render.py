"""
Задачи Celery для рендеринга документов.
"""
import logging
import time
import json
import requests
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from celery import shared_task, Task
from celery.exceptions import MaxRetriesExceededError, SoftTimeLimitExceeded
from reversion.models import Version

from apps.generation.models import RenderTask, GeneratedDocument
from infrastructure.ceph import ceph_client
from infrastructure.renderers.render_client import RendererClient, RendererError

logger = logging.getLogger(__name__)


class RenderTaskBase(Task):
    """
    Базовый класс для задач рендеринга документов.
    
    Содержит общую логику обработки ошибок и обновления статусов.
    """
    abstract = True
    max_retries = 3
    default_retry_delay = 60  # 1 минута
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Обработка ошибки задачи."""
        render_task_id = args[0]
        try:
            render_task = RenderTask.objects.get(id=render_task_id)
            render_task.status = 'failed'
            render_task.error = str(exc)
            render_task.finished_at = timezone.now()
            render_task.save(update_fields=['status', 'error', 'finished_at'])
            
            # Отправка WebSocket обновления
            self._send_ws_update(render_task_id, {
                'status': 'failed',
                'error': str(exc),
                'progress': render_task.progress
            })
            
            logger.error(f"Render task {render_task_id} failed: {exc}")
        except Exception as e:
            logger.error(f"Failed to update render task {render_task_id} on failure: {e}")
    
    def _update_progress(self, task_id, progress):
        """Обновляет прогресс задачи и отправляет WebSocket уведомление."""
        try:
            render_task = RenderTask.objects.get(id=task_id)
            render_task.progress = progress
            render_task.save(update_fields=['progress'])
            
            # Отправка WebSocket обновления
            self._send_ws_update(task_id, {
                'status': render_task.status,
                'progress': progress
            })
        except Exception as e:
            logger.error(f"Failed to update render task {task_id} progress: {e}")
    
    def _send_ws_update(self, task_id, data):
        """Отправляет обновления о статусе задачи через WebSocket."""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"task_{task_id}",
                {
                    'type': 'task_progress',
                    'message': data
                }
            )
        except Exception as e:
            logger.error(f"Failed to send WebSocket update for task {task_id}: {e}")


class RenderingMixin:
    """Миксин для общей логики рендеринга."""
    
    def _render_document(self, task_id, html, options, format_type, renderer_url=None):
        """
        Общая логика рендеринга документа.
        
        Args:
            task_id: ID задачи рендеринга
            html: HTML для рендеринга
            options: Опции рендеринга
            format_type: Тип формата (pdf, png, svg)
            renderer_url: URL рендерера
        """
        logger.info(f"Starting {format_type.upper()} rendering for task {task_id}")
        
        try:
            # Получаем задачу и формат
            render_task = RenderTask.objects.get(id=task_id)
            format_obj = render_task.template.format
            
            # Обновляем статус задачи
            render_task.status = 'processing'
            render_task.save(update_fields=['status'])
            
            # Отправляем WebSocket уведомление
            self._send_ws_update(task_id, {
                'status': 'processing',
                'progress': 10
            })
            
            # Создаем клиент рендерера с объектом Format
            renderer = RendererClient(format_type, format_obj=format_obj)
            
            # Обновляем прогресс
            self._update_progress(task_id, 30)
            
            # Выполняем рендеринг
            document_bytes, content_type = renderer.render(html, options)
            
            # Обновляем прогресс
            self._update_progress(task_id, 70)
            
            # Создаем запись документа
            document = self._create_document_record(
                task_id, 
                document_bytes, 
                f"document.{format_type}", 
                content_type
            )
            
            # Обновляем прогресс
            self._update_progress(task_id, 90)
            
            # Завершаем задачу
            render_task.mark_as_done()
            
            # Отправляем финальное WebSocket уведомление
            self._send_ws_update(task_id, {
                'status': 'done',
                'progress': 100,
                'document_id': str(document.id),
                'file_url': document.file
            })
            
            logger.info(f"{format_type.upper()} rendering completed for task {task_id}")
            return str(document.id)
            
        except RendererError as e:
            logger.error(f"Renderer error for task {task_id}: {e}")
            self._handle_render_error(task_id, e)
            
        except SoftTimeLimitExceeded:
            logger.error(f"Rendering timeout for task {task_id}")
            self._handle_timeout(task_id)
            
        except Exception as e:
            logger.error(f"Unexpected error in rendering task {task_id}: {e}")
            self._handle_unexpected_error(task_id, e)
    
    def _handle_render_error(self, task_id, error):
        """Обрабатывает ошибки рендерера."""
        try:
            render_task = RenderTask.objects.get(id=task_id)
            render_task.mark_as_failed(f"Ошибка рендеринга: {str(error)}")
            
            # Определяем, стоит ли повторять попытку
            if "timeout" in str(error).lower() and self.request.retries < self.max_retries:
                self.retry(countdown=self.default_retry_delay * (self.request.retries + 1))
            else:
                raise
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for task {task_id}")
            raise
    
    def _handle_timeout(self, task_id):
        """Обрабатывает таймаут."""
        try:
            render_task = RenderTask.objects.get(id=task_id)
            render_task.mark_as_failed("Превышено время ожидания рендеринга")
            raise SoftTimeLimitExceeded()
        except Exception as e:
            logger.error(f"Error handling timeout for task {task_id}: {e}")
            raise
    
    def _handle_unexpected_error(self, task_id, error):
        """Обрабатывает неожиданные ошибки."""
        try:
            if self.request.retries < self.max_retries:
                delay = self.default_retry_delay * (self.request.retries + 1)
                logger.info(f"Retrying task {task_id} in {delay} seconds")
                self.retry(countdown=delay)
            else:
                raise MaxRetriesExceededError(f"Max retries exceeded: {str(error)}")
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for task {task_id}")
            raise


@shared_task(bind=True, base=RenderTaskBase, time_limit=180)
def render_pdf(self, task_id, html, options, renderer_url=None):
    """Генерирует PDF документ."""
    return self._render_document(task_id, html, options, 'pdf', renderer_url)


@shared_task(bind=True, base=RenderTaskBase, time_limit=180)
def render_png(self, task_id, html, options, renderer_url=None):
    """Генерирует PNG документ."""
    return self._render_document(task_id, html, options, 'png', renderer_url)


@shared_task(bind=True, base=RenderTaskBase, time_limit=180)
def render_svg(self, task_id, html, options, renderer_url=None):
    """Генерирует SVG документ."""
    return self._render_document(task_id, html, options, 'svg', renderer_url)


# Применяем миксин к задачам
for task in [render_pdf, render_png, render_svg]:
    task.__class__ = type(task.__class__.__name__, (RenderingMixin, task.__class__), {})