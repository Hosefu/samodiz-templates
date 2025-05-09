"""
Сервис для генерации документов.
"""
import logging
from typing import Dict, Any, Optional
from django.db import transaction
from django.utils import timezone
from reversion.models import Version

from apps.templates.models.template import Template
from apps.templates.services.templating import template_renderer
from apps.generation.models import RenderTask
from apps.generation.tasks.render import render_pdf, render_png, render_svg

logger = logging.getLogger(__name__)


class DocumentGenerationError(Exception):
    """Исключение для ошибок генерации документов."""
    pass


class DocumentGenerationService:
    """Сервис для генерации документов."""
    
    # Маппинг форматов к задачам Celery
    FORMAT_TASKS = {
        'pdf': render_pdf,
        'png': render_png,
        'svg': render_svg,
    }
    
    @classmethod
    def generate_document(
        cls,
        template: Template,
        data: Dict[str, Any],
        user,
        request_ip: str
    ) -> RenderTask:
        """
        Генерирует документ на основе шаблона.
        
        Args:
            template: Шаблон для генерации
            data: Данные для подстановки
            user: Пользователь, запросивший генерацию
            request_ip: IP адрес запроса
            
        Returns:
            RenderTask: Созданная задача рендеринга
            
        Raises:
            DocumentGenerationError: При ошибке генерации
        """
        try:
            with transaction.atomic():
                # Создаем задачу рендеринга (без создания версии)
                task = cls._create_render_task(template, user, request_ip, data)
                
                # Подготавливаем данные для рендеринга
                rendered_html = cls._prepare_template_html(template, data)
                options = cls._prepare_render_options(template)
                
                # Запускаем задачу рендеринга
                cls._start_render_task(task, rendered_html, options, template.format)
                
                return task
                
        except Exception as e:
            logger.error(f"Error generating document: {e}")
            raise DocumentGenerationError(f"Ошибка генерации документа: {str(e)}") from e
    
    @staticmethod
    def _create_render_task(
        template: Template,
        user,
        request_ip: str,
        data: Dict[str, Any]
    ) -> RenderTask:
        """Создает задачу рендеринга."""
        # Если нужно сохранить информацию о версии шаблона - берем текущую
        version = Version.objects.get_for_object(template).first()
        
        return RenderTask.objects.create(
            template=template,
            version_id=version.id if version else None,  # Сохраняем версию шаблона для истории
            user=user if not user.is_anonymous else None,
            request_ip=request_ip,
            data_input=data,
            status='pending',
            progress=0,
        )
    
    @staticmethod
    def _prepare_template_html(template: Template, data: Dict[str, Any]) -> str:
        """Подготавливает HTML шаблона со всеми страницами."""
        pages_html = []
        
        for page in template.pages.all().order_by('index'):
            # Используем HTML страницы или базовый шаблон
            page_html = page.html if page.html else template.html
            
            # Рендерим страницу с данными
            try:
                rendered_page = template_renderer.render_template(
                    page_html, 
                    data, 
                    template_id=str(template.id),
                    page_id=str(page.id)
                )
                pages_html.append(rendered_page)
            except Exception as e:
                logger.error(f"Error rendering page {page.index}: {e}")
                raise DocumentGenerationError(f"Ошибка рендеринга страницы {page.index}: {str(e)}")
        
        return ''.join(pages_html)
    
    @staticmethod
    def _prepare_render_options(template: Template) -> Dict[str, Any]:
        """Подготавливает опции для рендеринга."""
        first_page = template.pages.first()
        if not first_page:
            raise DocumentGenerationError("Шаблон не содержит ни одной страницы")
        
        # Базовые опции
        options = {
            'format': template.format.name.lower(),
            'width': float(first_page.width),
            'height': float(first_page.height),
            'unit': template.unit.key,
        }
        
        # Добавляем настройки формата
        for page in template.pages.all():
            for setting in page.settings.all():
                options[setting.format_setting.key] = setting.value
        
        return options
    
    @classmethod
    def _start_render_task(
        cls,
        task: RenderTask,
        html: str,
        options: Dict[str, Any],
        format_obj: 'Format'  # Передаем весь объект Format
    ):
        """Запускает задачу рендеринга."""
        # Получаем соответствующую задачу Celery
        celery_task_func = cls.FORMAT_TASKS.get(format_obj.name.lower())
        if not celery_task_func:
            raise DocumentGenerationError(f"Неподдерживаемый формат: {format_obj.name}")
        
        # Используем URL рендерера из формата
        renderer_url = format_obj.render_url
        
        # Запускаем задачу Celery
        celery_task = celery_task_func.delay(
            str(task.id),
            html,
            options,
            renderer_url
        )
        
        # Сохраняем ID задачи Celery
        task.worker_id = celery_task.id
        task.save(update_fields=['worker_id']) 