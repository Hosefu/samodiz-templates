"""
Задачи Celery для рендеринга документов (PDF, PNG, SVG).
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

from apps.generation.models import RenderTask, Document
from infrastructure.ceph import ceph_client
from infrastructure.renderers.render_client import RendererClient

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


@shared_task(bind=True, base=RenderTaskBase, time_limit=180)
def render_pdf(self, task_id, html, options):
    """
    Генерирует PDF документ на основе HTML.
    
    Args:
        task_id: ID задачи RenderTask
        html: HTML-код для рендеринга
        options: Опции для рендеринга (формат, размеры и т.д.)
    """
    logger.info(f"Starting PDF rendering for task {task_id}")
    
    try:
        # Получаем задачу из БД
        render_task = RenderTask.objects.get(id=task_id)
        
        # Обновляем статус
        render_task.status = 'processing'
        render_task.save(update_fields=['status'])
        
        # Отправляем WebSocket обновление
        self._send_ws_update(task_id, {
            'status': 'processing',
            'progress': 10
        })
        
        # Создаем клиент рендерера
        renderer = RendererClient('pdf')
        
        # Отправляем запрос на рендеринг
        self._update_progress(task_id, 30)
        
        # Выполняем рендеринг
        pdf_bytes, content_type = renderer.render(html, options)
        
        # Обновляем прогресс
        self._update_progress(task_id, 70)
        
        # Загружаем результат в Ceph
        template_name = render_task.template.name
        file_name = f"{template_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        key, url = ceph_client.upload_file(
            file_obj=pdf_bytes,
            folder=f"documents/{task_id}",
            filename=file_name,
            content_type=content_type
        )
        
        # Обновляем прогресс
        self._update_progress(task_id, 90)
        
        # Создаем запись о документе
        document = Document.objects.create(
            task=render_task,
            file=url,
            size_bytes=len(pdf_bytes),
            file_name=file_name,
            content_type=content_type
        )
        
        # Завершаем задачу
        render_task.status = 'done'
        render_task.progress = 100
        render_task.finished_at = timezone.now()
        render_task.save(update_fields=['status', 'progress', 'finished_at'])
        
        # Отправляем финальное WebSocket обновление
        self._send_ws_update(task_id, {
            'status': 'done',
            'progress': 100,
            'document_id': str(document.id),
            'file_url': url
        })
        
        logger.info(f"PDF rendering completed for task {task_id}")
        return str(document.id)
    
    except SoftTimeLimitExceeded:
        logger.error(f"PDF rendering timeout for task {task_id}")
        raise
    except Exception as e:
        logger.error(f"Error in PDF rendering for task {task_id}: {e}")
        
        try:
            self.retry(countdown=self.default_retry_delay * (self.request.retries + 1))
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for PDF rendering task {task_id}")
            raise
        
        raise


@shared_task(bind=True, base=RenderTaskBase, time_limit=180)
def render_png(self, task_id, html, options):
    """
    Генерирует PNG документ на основе HTML.
    
    Args:
        task_id: ID задачи RenderTask
        html: HTML-код для рендеринга
        options: Опции для рендеринга (формат, размеры и т.д.)
    """
    logger.info(f"Starting PNG rendering for task {task_id}")
    
    try:
        # Получаем задачу из БД
        render_task = RenderTask.objects.get(id=task_id)
        
        # Обновляем статус
        render_task.status = 'processing'
        render_task.save(update_fields=['status'])
        
        # Отправляем WebSocket обновление
        self._send_ws_update(task_id, {
            'status': 'processing',
            'progress': 10
        })
        
        # Создаем клиент рендерера
        renderer = RendererClient('png')
        
        # Отправляем запрос на рендеринг
        self._update_progress(task_id, 30)
        
        # Выполняем рендеринг
        png_bytes, content_type = renderer.render(html, options)
        
        # Обновляем прогресс
        self._update_progress(task_id, 70)
        
        # Загружаем результат в Ceph
        template_name = render_task.template.name
        file_name = f"{template_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        key, url = ceph_client.upload_file(
            file_obj=png_bytes,
            folder=f"documents/{task_id}",
            filename=file_name,
            content_type=content_type
        )
        
        # Обновляем прогресс
        self._update_progress(task_id, 90)
        
        # Создаем запись о документе
        document = Document.objects.create(
            task=render_task,
            file=url,
            size_bytes=len(png_bytes),
            file_name=file_name,
            content_type=content_type
        )
        
        # Завершаем задачу
        render_task.status = 'done'
        render_task.progress = 100
        render_task.finished_at = timezone.now()
        render_task.save(update_fields=['status', 'progress', 'finished_at'])
        
        # Отправляем финальное WebSocket обновление
        self._send_ws_update(task_id, {
            'status': 'done',
            'progress': 100,
            'document_id': str(document.id),
            'file_url': url
        })
        
        logger.info(f"PNG rendering completed for task {task_id}")
        return str(document.id)
    
    except SoftTimeLimitExceeded:
        logger.error(f"PNG rendering timeout for task {task_id}")
        raise
    except Exception as e:
        logger.error(f"Error in PNG rendering for task {task_id}: {e}")
        
        try:
            self.retry(countdown=self.default_retry_delay * (self.request.retries + 1))
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for PNG rendering task {task_id}")
            raise
        
        raise


@shared_task(bind=True, base=RenderTaskBase, time_limit=180)
def render_svg(self, task_id, html, options):
    """
    Генерирует SVG документ на основе HTML.
    
    Args:
        task_id: ID задачи RenderTask
        html: HTML-код для рендеринга
        options: Опции для рендеринга (формат, размеры и т.д.)
    """
    logger.info(f"Starting SVG rendering for task {task_id}")
    
    try:
        # Получаем задачу из БД
        render_task = RenderTask.objects.get(id=task_id)
        
        # Обновляем статус
        render_task.status = 'processing'
        render_task.save(update_fields=['status'])
        
        # Отправляем WebSocket обновление
        self._send_ws_update(task_id, {
            'status': 'processing',
            'progress': 10
        })
        
        # Создаем клиент рендерера
        renderer = RendererClient('svg')
        
        # Отправляем запрос на рендеринг
        self._update_progress(task_id, 30)
        
        # Выполняем рендеринг
        svg_bytes, content_type = renderer.render(html, options)
        
        # Обновляем прогресс
        self._update_progress(task_id, 70)
        
        # Загружаем результат в Ceph
        template_name = render_task.template.name
        file_name = f"{template_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.svg"
        key, url = ceph_client.upload_file(
            file_obj=svg_bytes,
            folder=f"documents/{task_id}",
            filename=file_name,
            content_type=content_type
        )
        
        # Обновляем прогресс
        self._update_progress(task_id, 90)
        
        # Создаем запись о документе
        document = Document.objects.create(
            task=render_task,
            file=url,
            size_bytes=len(svg_bytes),
            file_name=file_name,
            content_type=content_type
        )
        
        # Завершаем задачу
        render_task.status = 'done'
        render_task.progress = 100
        render_task.finished_at = timezone.now()
        render_task.save(update_fields=['status', 'progress', 'finished_at'])
        
        # Отправляем финальное WebSocket обновление
        self._send_ws_update(task_id, {
            'status': 'done',
            'progress': 100,
            'document_id': str(document.id),
            'file_url': url
        })
        
        logger.info(f"SVG rendering completed for task {task_id}")
        return str(document.id)
    
    except SoftTimeLimitExceeded:
        logger.error(f"SVG rendering timeout for task {task_id}")
        raise
    except Exception as e:
        logger.error(f"Error in SVG rendering for task {task_id}: {e}")
        
        try:
            self.retry(countdown=self.default_retry_delay * (self.request.retries + 1))
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for SVG rendering task {task_id}")
            raise
        
        raise