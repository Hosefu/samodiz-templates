from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction
from apps.templates.models import Template, Page
from apps.templates.tasks import render_template_task

class TemplateRenderService:
    def __init__(self):
        self.channel_layer = get_channel_layer()

    async def render_template(self, template_id, group_name):
        # Получаем шаблон
        template = await self._get_template(template_id)
        if not template:
            return

        # Отправляем начальный статус
        await self._send_progress(group_name, 0, 'started')

        try:
            # Запускаем задачу рендеринга
            task = render_template_task.delay(template_id)
            
            # Отслеживаем прогресс
            while not task.ready():
                progress = task.info.get('progress', 0)
                status = task.info.get('status', 'processing')
                await self._send_progress(group_name, progress, status)
                
                if task.failed():
                    raise Exception(task.result)

            # Отправляем финальный статус
            await self._send_progress(group_name, 100, 'completed')

        except Exception as e:
            await self._send_progress(group_name, 0, f'error: {str(e)}')

    async def _send_progress(self, group_name, progress, status):
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'render_progress',
                'progress': progress,
                'status': status
            }
        )

    @transaction.atomic
    def _get_template(self, template_id):
        try:
            return Template.objects.select_related(
                'format',
                'format__unit'
            ).prefetch_related(
                'pages',
                'pages__fields',
                'pages__assets'
            ).get(id=template_id)
        except Template.DoesNotExist:
            return None
 