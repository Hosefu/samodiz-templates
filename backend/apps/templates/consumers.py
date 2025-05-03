import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.templates.models import Template
from apps.templates.services.template_render_service import TemplateRenderService

class TemplateRenderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.template_id = self.scope['url_route']['kwargs']['template_id']
        self.template_group_name = f'template_{self.template_id}'
        
        # Проверяем существование шаблона
        if not await self.template_exists():
            await self.close()
            return
            
        # Присоединяемся к группе
        await self.channel_layer.group_add(
            self.template_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Отсоединяемся от группы
        await self.channel_layer.group_discard(
            self.template_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        
        if action == 'start_render':
            # Запускаем рендеринг
            render_service = TemplateRenderService()
            await render_service.render_template(
                self.template_id,
                self.template_group_name
            )

    async def render_progress(self, event):
        # Отправляем прогресс клиенту
        await self.send(text_data=json.dumps({
            'type': 'progress',
            'progress': event['progress'],
            'status': event['status']
        }))

    @database_sync_to_async
    def template_exists(self):
        return Template.objects.filter(id=self.template_id).exists() 