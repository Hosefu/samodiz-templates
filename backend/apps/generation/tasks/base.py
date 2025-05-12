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
from pathlib import Path
from django.conf import settings

from apps.generation.models import RenderTask, GeneratedDocument
from infrastructure.minio_client import minio_client
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
        """Отправляет обновление статуса через WebSocket."""
        try:
            async_to_sync(self.channel_layer.group_send)(
                f"render_task_{task_id}",
                {
                    'type': 'render_task_update',
                    'message': data
                }
            )
        except Exception as e:
            logger.error(f"Failed to send WebSocket update: {e}")
    
    def _create_document_record(self, task_id, file_bytes, file_name, content_type):
        """Создает запись документа в БД."""
        try:
            render_task = RenderTask.objects.get(id=task_id)
            template_name = render_task.template.name
            
            # Генерируем имя файла
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            safe_template_name = template_name.replace(' ', '_')
            file_name = f"{safe_template_name}_{timestamp}.{file_name.split('.')[-1]}"
            
            # Загружаем файл в MinIO
            object_name, url = minio_client.upload_file(
                file_obj=file_bytes,
                folder=f"documents/{task_id}",
                filename=file_name,
                content_type=content_type,
                bucket_type='documents'
            )
            
            # Создаем запись документа
            document = GeneratedDocument.objects.create(
                task=render_task,
                file=url,
                size_bytes=len(file_bytes.getvalue()) if hasattr(file_bytes, 'getvalue') else file_bytes.getbuffer().nbytes,
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
        """
        logger.info(f"Starting {format_type.upper()} rendering for task {task_id}")
        
        # Добавляем логирование HTML (только начало и конец, чтобы не засорять логи)
        html_preview = html[:500] + "..." if len(html) > 500 else html
        logger.debug(f"HTML for rendering (preview):\n{html_preview}")
        
        # Для отладки можно временно писать полный HTML в файл
        if settings.DEBUG:
            debug_file = Path(settings.BASE_DIR) / 'logs' / f'render_debug_{task_id}.html'
            debug_file.parent.mkdir(exist_ok=True)
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Full HTML saved to: {debug_file}")
        
        render_task = RenderTask.objects.get(id=task_id)
        client = RendererClient(format_type, renderer_url=renderer_url)
        
        try:
            # Обновляем статус
            render_task.mark_as_processing()
            
            # Отправляем WebSocket уведомление
            self._send_ws_update(task_id, {
                'status': 'processing',
                'progress': render_task.progress
            })
            
            # Рендерим документ - используем правильное имя метода render
            rendered_data, content_type = client.render(html, options)
            
            # Сохраняем результат
            if not rendered_data:
                raise RendererError("Empty response from renderer")
            
            # Создаем запись документа в БД
            document = self._create_document_record(
                task_id=task_id,
                file_bytes=rendered_data,
                file_name=f"document.{format_type}",
                content_type=content_type  # Используем возвращенный content_type
            )
            
            # Обновляем статус задачи
            render_task.mark_as_done()
            
            # Отправляем WebSocket уведомление
            self._send_ws_update(task_id, {
                'status': 'done',
                'document_url': document.file,
                'progress': 100
            })
            
            logger.info(f"Document rendered successfully: {document.file}")
            return document.file
            
        except Exception as e:
            logger.error(f"Error rendering document: {e}")
            render_task.mark_as_failed(str(e))
            
            # Отправляем WebSocket уведомление
            self._send_ws_update(task_id, {
                'status': 'failed',
                'error': str(e),
                'progress': render_task.progress
            })
            
            # Повторяем задачу, если не превышен лимит повторов
            raise self.retry(exc=e)
    
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