"""
Сервис для генерации документов.
Координирует весь процесс от получения данных до запуска задачи рендеринга.
"""
import logging
from typing import Dict, Any, Optional
from django.db import transaction
from django.utils import timezone
from reversion import revisions
from reversion.models import Version

from apps.templates.models.template import Template
from apps.templates.models.unit_format import Format
from apps.templates.services.templating import template_renderer
from apps.generation.models import RenderTask
from apps.generation.tasks.render import render_pdf, render_png, render_svg

logger = logging.getLogger(__name__)


class DocumentGenerationService:
    """Сервис для генерации документов."""
    
    @staticmethod
    def _get_or_create_template_version(template: Template, user) -> Version:
        """Получает или создает версию шаблона."""
        # Получаем текущую версию шаблона
        versions = Version.objects.get_for_object(template)
        current_version = versions.first()
        
        # Если версии нет, создаем
        if not current_version:
            try:
                with revisions.create_revision():
                    template.save()
                    revisions.set_user(user)
                    revisions.set_comment("Auto-created during document generation")
                
                # Перезапрашиваем версию после создания
                current_version = Version.objects.get_for_object(template).first()
                
                if not current_version:
                    raise RuntimeError("Failed to create template version")
                    
            except Exception as e:
                logger.error(f"Error creating version: {e}")
                raise RuntimeError(f"Ошибка создания версии шаблона: {str(e)}")
        
        return current_version
    
    @staticmethod
    def _prepare_html(template: Template, data: Dict[str, Any]) -> str:
        """Подготавливает HTML со всеми страницами."""
        pages_html = []
        
        for page in template.pages.all().order_by('index'):
            # Получаем HTML страницы (если у страницы нет HTML, используем базовый шаблон)
            page_html = page.html if page.html else template.html
            
            # Рендерим страницу с учетом локальных ассетов
            rendered_page_html = template_renderer.render_template(
                page_html, 
                data, 
                template_id=template.id,
                page_id=page.id
            )
            
            pages_html.append(rendered_page_html)
        
        return ''.join(pages_html)
    
    @staticmethod
    def _prepare_render_options(template: Template) -> Dict[str, Any]:
        """Подготавливает опции для рендеринга."""
        # Базовые опции
        first_page = template.pages.first()
        if not first_page:
            raise RuntimeError("Шаблон не содержит ни одной страницы")
        
        options = {
            'format': template.format.name.lower(),
            'width': float(first_page.width),
            'height': float(first_page.height),
            'unit': template.unit.key,
        }
        
        # Добавляем специфичные настройки формата
        format_settings = {}
        for page in template.pages.all():
            for setting in page.settings.all():
                format_settings[setting.format_setting.key] = setting.value
        
        options.update(format_settings)
        
        return options
    
    @staticmethod
    def generate_document(
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
        """
        try:
            with transaction.atomic():
                # 1. Получаем или создаем версию шаблона
                current_version = DocumentGenerationService._get_or_create_template_version(template, user)
                
                # 2. Создаем задачу рендеринга
                task = RenderTask.objects.create(
                    template=template,
                    version_id=current_version.id,
                    user=user,
                    request_ip=request_ip,
                    data_input={'data': data},
                    status='pending',
                    progress=0,
                )
                
                # 3. Подготавливаем HTML
                rendered_html = DocumentGenerationService._prepare_html(template, data)
                
                # 4. Подготавливаем опции рендеринга
                options = DocumentGenerationService._prepare_render_options(template)
                
                # 5. Получаем формат и URL рендерера
                format_name = template.format.name.lower()
                format_obj = Format.objects.get(name=format_name)
                renderer_url = format_obj.render_url
                
                # 6. Запускаем соответствующую задачу Celery
                if format_name == 'pdf':
                    celery_task = render_pdf.delay(str(task.id), rendered_html, options, renderer_url)
                elif format_name == 'png':
                    celery_task = render_png.delay(str(task.id), rendered_html, options, renderer_url)
                elif format_name == 'svg':
                    celery_task = render_svg.delay(str(task.id), rendered_html, options, renderer_url)
                else:
                    raise ValueError(f"Неподдерживаемый формат: {format_name}")
                
                # 7. Сохраняем ID задачи Celery
                task.worker_id = celery_task.id
                task.save(update_fields=['worker_id'])
                
                return task
                
        except Exception as e:
            logger.error(f"Error generating document: {e}")
            raise 