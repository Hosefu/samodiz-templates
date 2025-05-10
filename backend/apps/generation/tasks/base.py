"""
Базовый класс для задач рендеринга.
"""
import logging
from datetime import datetime
from celery import Task
from celery.exceptions import MaxRetriesExceededError, SoftTimeLimitExceeded
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from apps.generation.models import RenderTask, GeneratedDocument
from infrastructure.ceph import ceph_client
from infrastructure.renderers.render_client import RendererClient

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