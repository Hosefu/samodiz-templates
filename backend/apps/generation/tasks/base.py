"""
Базовый класс для задач рендеринга.
"""
import logging
from datetime import datetime
from celery import Task
from celery.exceptions import MaxRetriesExceededError, SoftTimeLimitExceeded
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import requests

from apps.generation.models import RenderTask, GeneratedDocument
from infrastructure.ceph import ceph_client
from infrastructure.renderers.render_client import RendererClient, RendererError

logger = logging.getLogger(__name__)


class RenderTaskBase(Task):
    """
    Базовый класс для задач рендеринга документов.
    """
    abstract = True
    max_retries = 3
    default_retry_delay = 60
    
    def __init__(self):
        super().__init__()
        self.channel_layer = get_channel_layer()
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Обработка ошибки задачи."""
        render_task_id = args[0]
        try:
            render_task = RenderTask.objects.get(id=render_task_id)
            render_task.mark_as_failed(str(exc))
            
            # Отправляем WebSocket уведомление
            self._send_ws_update(render_task_id, {
                'status': 'failed',
                'error': str(exc),
                'progress': render_task.progress
            })
            
            logger.error(f"Render task {render_task_id} failed: {exc}")
        except Exception as e:
            logger.error(f"Failed to update render task {render_task_id} on failure: {e}")
    
    def _update_progress(self, task_id, progress):
        """Обновляет прогресс задачи."""
        try:
            render_task = RenderTask.objects.get(id=task_id)
            render_task.update_progress(progress)
            
            self._send_ws_update(task_id, {
                'status': render_task.status,
                'progress': progress
            })
        except Exception as e:
            logger.error(f"Failed to update render task {task_id} progress: {e}")
    
    def _send_ws_update(self, task_id, data):
        """Отправляет обновления через WebSocket."""
        try:
            async_to_sync(self.channel_layer.group_send)(
                f"task_{task_id}",
                {
                    'type': 'task_progress',
                    'message': data
                }
            )
        except Exception as e:
            logger.error(f"Failed to send WebSocket update for task {task_id}: {e}")
    
    def _create_document_record(self, task_id, file_bytes, file_name, content_type):
        """Создает запись документа в БД."""
        try:
            render_task = RenderTask.objects.get(id=task_id)
            template_name = render_task.template.name
            
            # Генерируем имя файла
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            safe_template_name = template_name.replace(' ', '_')
            file_name = f"{safe_template_name}_{timestamp}.{file_name.split('.')[-1]}"
            
            # Загружаем файл в Ceph
            key, url = ceph_client.upload_file(
                file_obj=file_bytes,
                folder=f"documents/{task_id}",
                filename=file_name,
                content_type=content_type
            )
            
            # Создаем запись документа
            document = GeneratedDocument.objects.create(
                task=render_task,
                file=url,
                size_bytes=len(file_bytes.getvalue()) if hasattr(file_bytes, 'getvalue') else len(file_bytes),
                file_name=file_name,
                content_type=content_type
            )
            
            return document
            
        except Exception as e:
            logger.error(f"Failed to create document record: {e}")
            raise
    
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