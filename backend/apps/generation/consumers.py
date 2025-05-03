"""
WebSocket потребители для отслеживания прогресса генерации документов.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.generation.models import RenderTask

logger = logging.getLogger(__name__)


class TaskProgressConsumer(AsyncWebsocketConsumer):
    """
    WebSocket потребитель для отслеживания прогресса задач рендеринга в реальном времени.
    """
    
    async def connect(self):
        """Обработчик подключения клиента WebSocket."""
        # Получаем ID задачи из URL
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.group_name = f"task_{self.task_id}"
        
        # Проверяем существование задачи и права доступа
        task_exists = await self.check_task_exists()
        if not task_exists:
            logger.warning(f"WebSocket connection rejected: Task {self.task_id} not found")
            await self.close()
            return
        
        # Присоединяемся к группе для получения обновлений
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        # Принимаем подключение
        await self.accept()
        
        # Отправляем текущее состояние задачи
        task_data = await self.get_task_data()
        await self.send_task_status(task_data)
    
    async def disconnect(self, close_code):
        """Обработчик отключения клиента WebSocket."""
        # Покидаем группу
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Обработчик входящих сообщений (не используется)."""
        # Клиенты не должны отправлять сообщения, поэтому игнорируем
        pass
    
    async def task_progress(self, event):
        """
        Обработчик сообщений о прогрессе задачи.
        
        Получает обновления от Celery задачи и отправляет их клиенту.
        """
        # Отправляем сообщение клиенту
        await self.send(text_data=json.dumps(event['message']))
    
    async def send_task_status(self, task_data):
        """Отправляет текущее состояние задачи клиенту."""
        if task_data:
            await self.send(text_data=json.dumps(task_data))
    
    @database_sync_to_async
    def check_task_exists(self):
        """Проверяет существование задачи."""
        try:
            return RenderTask.objects.filter(id=self.task_id).exists()
        except Exception as e:
            logger.error(f"Error checking task existence: {e}")
            return False
    
    @database_sync_to_async
    def get_task_data(self):
        """Получает текущие данные о задаче."""
        try:
            task = RenderTask.objects.get(id=self.task_id)
            
            data = {
                'status': task.status,
                'progress': task.progress,
            }
            
            # Добавляем информацию об ошибке, если есть
            if task.status == 'failed' and task.error:
                data['error'] = task.error
            
            # Добавляем информацию о документе, если задача выполнена
            if task.status == 'done' and task.documents.exists():
                document = task.documents.first()
                data['document_id'] = str(document.id)
                data['file_url'] = document.file
            
            return data
        
        except RenderTask.DoesNotExist:
            logger.warning(f"Task {self.task_id} not found when trying to get data")
            return None
        except Exception as e:
            logger.error(f"Error getting task data: {e}")
            return None