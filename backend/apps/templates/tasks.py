from celery import shared_task
from django.db import transaction
from apps.templates.models import Template
from apps.templates.services.template_render_service import TemplateRenderService

@shared_task(bind=True)
def render_template_task(self, template_id):
    """
    Задача для асинхронного рендеринга шаблона.
    """
    try:
        # Получаем шаблон
        template = Template.objects.select_related(
            'format',
            'format__unit'
        ).prefetch_related(
            'pages',
            'pages__fields',
            'pages__assets'
        ).get(id=template_id)

        # Создаем рендерер
        renderer = TemplateRenderService()

        # Обновляем прогресс
        self.update_state(
            state='PROGRESS',
            meta={
                'progress': 0,
                'status': 'initializing'
            }
        )

        # Рендерим шаблон
        result = renderer.render(template)

        # Обновляем прогресс
        self.update_state(
            state='PROGRESS',
            meta={
                'progress': 100,
                'status': 'completed'
            }
        )

        return result

    except Exception as e:
        # Обновляем прогресс с ошибкой
        self.update_state(
            state='FAILURE',
            meta={
                'progress': 0,
                'status': f'error: {str(e)}'
            }
        )
        raise 