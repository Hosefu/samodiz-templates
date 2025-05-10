"""
Представления API для генерации документов.
"""
import logging
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status, views, viewsets, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django_filters import rest_framework as filters
from rest_framework.decorators import action
from reversion import revisions
from reversion.models import Version

from apps.templates.models.template import Template
from apps.templates.api.permissions import IsPublicTemplateOrAuthenticated
from apps.templates.services.templating import template_renderer
from apps.generation.models import RenderTask, Document
from apps.generation.api.serializers import (
    RenderTaskSerializer, RenderTaskDetailSerializer,
    DocumentSerializer, DocumentDetailSerializer,
    GenerateDocumentSerializer
)
from apps.generation.tasks.render import render_pdf, render_png, render_svg

logger = logging.getLogger(__name__)


def validate_template_syntax(html_content, data_sample=None):
    """Валидирует синтаксис Jinja шаблона."""
    try:
        from apps.templates.services.templating import template_renderer
        
        # Проверяем синтаксис
        errors = template_renderer.validate_template(html_content)
        if errors:
            return False, errors
            
        # Пробуем рендерить с пустыми данными
        test_data = data_sample or {}
        template_renderer.render_template(html_content, test_data)
        
        return True, None
    except Exception as e:
        return False, str(e)


class GenerateDocumentView(views.APIView):
    """
    API для генерации документов на основе шаблонов.
    
    Принимает данные для подстановки в шаблон и запускает асинхронную задачу рендеринга.
    """
    permission_classes = [IsPublicTemplateOrAuthenticated]
    
    def _get_client_ip(self, request):
        """Получает IP-адрес клиента."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def post(self, request, template_id):
        """Запускает генерацию документа на основе шаблона."""
        # Получаем шаблон
        template = get_object_or_404(Template, id=template_id)
        
        # Проверяем данные запроса
        serializer = GenerateDocumentSerializer(data=request.data, context={'template': template})
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                # Получаем текущую версию шаблона
                versions = Version.objects.get_for_object(template)
                current_version = versions.first()  # Последняя версия
                
                # Если версии нет, создаем
                if not current_version:
                    with revisions.create_revision():
                        template.save()
                        revisions.set_user(request.user if request.user.is_authenticated else None)
                        revisions.set_comment("Auto-created during document generation")
                        current_version = Version.objects.get_for_object(template).first()
                
                # Создаем задачу рендеринга
                task = RenderTask.objects.create(
                    template=template,
                    version_id=current_version.id,
                    user=request.user if request.user.is_authenticated else None,
                    request_ip=self._get_client_ip(request),
                    data_input=serializer.validated_data,
                    status='pending',
                    progress=0,
                )
                
                # Подготавливаем данные для рендеринга
                data = serializer.validated_data.get('data', {})
                
                # Применяем шаблонизатор к HTML, используя версию из reversion
                try:
                    # Получаем HTML шаблона из текущей версии
                    template_html = current_version.field_dict.get('html', template.html)
                    
                    # Логируем данные для диагностики
                    logger.info(f"Template HTML: {template_html[:200]}...")  # Первые 200 символов
                    logger.info(f"User data: {data}")
                    
                    # Валидируем шаблон
                    is_valid, validation_error = validate_template_syntax(template_html, data)
                    if not is_valid:
                        logger.error(f"Template validation failed: {validation_error}")
                        task.status = 'failed'
                        task.error = f"Ошибка валидации шаблона: {validation_error}"
                        task.finished_at = timezone.now()
                        task.save(update_fields=['status', 'error', 'finished_at'])
                        return Response(
                            {"detail": f"Ошибка валидации шаблона: {validation_error}"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Рендерим шаблон по страницам
                    pages_html = []
                    for page in template.pages.all().order_by('index'):
                        # Получаем HTML страницы
                        page_html = page.html if page.html else template_html
                        
                        # Логируем HTML страницы
                        logger.info(f"Page {page.index} HTML: {page_html[:200]}...")
                        
                        # Рендерим страницу с учетом локальных ассетов
                        rendered_page_html = template_renderer.render_template(
                            page_html, 
                            data, 
                            template_id=template.id,
                            page_id=page.id  # Передаем ID страницы для поиска локальных ассетов
                        )
                        
                        # Логируем результат рендеринга
                        logger.info(f"Rendered page {page.index}: {rendered_page_html[:200]}...")
                        
                        pages_html.append(rendered_page_html)
                    
                    # Объединяем все страницы
                    rendered_html = ''.join(pages_html)
                    
                except Exception as e:
                    logger.error(f"Template rendering error: {e}")
                    logger.error(f"Template HTML: {template_html}")
                    logger.error(f"User data: {data}")
                    logger.exception("Full error traceback:")
                    
                    task.status = 'failed'
                    task.error = f"Ошибка подготовки шаблона: {str(e)}"
                    task.finished_at = timezone.now()
                    task.save(update_fields=['status', 'error', 'finished_at'])
                    return Response(
                        {"detail": f"Ошибка подготовки шаблона: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Определяем, какую задачу запускать в зависимости от формата
                format_name = template.format.name.lower()
                
                # Опции для рендеринга
                first_page = template.pages.first()
                if not first_page:
                    task.status = 'failed'
                    task.error = "Шаблон не содержит ни одной страницы. Необходимо добавить хотя бы одну страницу."
                    task.finished_at = timezone.now()
                    task.save(update_fields=['status', 'error', 'finished_at'])
                    return Response(
                        {"detail": "Ошибка генерации документа: шаблон не содержит ни одной страницы"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                options = {
                    # Базовые опции
                    'format': format_name,
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
                
                # Запускаем соответствующую задачу Celery
                if format_name == 'pdf':
                    celery_task = render_pdf.delay(str(task.id), rendered_html, options)
                elif format_name == 'png':
                    celery_task = render_png.delay(str(task.id), rendered_html, options)
                elif format_name == 'svg':
                    celery_task = render_svg.delay(str(task.id), rendered_html, options)
                else:
                    task.status = 'failed'
                    task.error = f"Неподдерживаемый формат: {format_name}"
                    task.finished_at = timezone.now()
                    task.save(update_fields=['status', 'error', 'finished_at'])
                    return Response(
                        {"detail": f"Неподдерживаемый формат: {format_name}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Сохраняем ID задачи Celery
                task.worker_id = celery_task.id
                task.save(update_fields=['worker_id'])
                
                # Возвращаем ID задачи рендеринга
                return Response({
                    "id": str(task.id),
                    "status": task.status,
                    "message": "Задача рендеринга запущена"
                }, status=status.HTTP_202_ACCEPTED)
                
        except Exception as e:
            logger.error(f"Error generating document: {e}")
            return Response(
                {"detail": f"Ошибка генерации документа: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='fields')
    def get_template_fields(self, request, template_id=None):
        """Возвращает структурированный список полей шаблона."""
        template = get_object_or_404(Template, id=template_id)
        self.check_object_permissions(request, template)
        
        # Собираем все поля
        fields = template.fields.all().order_by('page__index', 'key')
        
        # Структурируем данные
        result = {
            'global_fields': [],
            'page_fields': {}
        }
        
        for field in fields:
            field_info = {
                'key': field.key,
                'label': field.label,
                'required': field.is_required,
            }
            
            if field.default_value:
                field_info['default_value'] = field.default_value
                
            if field.is_choices and field.choices:
                field_info['is_choices'] = True
                field_info['choices'] = field.choices
                
            if field.page is None:
                # Глобальное поле
                result['global_fields'].append(field_info)
            else:
                # Поле страницы
                page_key = str(field.page.index)
                if page_key not in result['page_fields']:
                    result['page_fields'][page_key] = []
                result['page_fields'][page_key].append(field_info)
        
        return Response(result)


class RenderTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для отслеживания задач рендеринга.
    
    Только чтение, задачи создаются через GenerateDocumentView.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Возвращает задачи пользователя."""
        user = self.request.user
        
        # Администраторы видят все задачи
        if user.is_staff:
            return RenderTask.objects.all().order_by('-started_at')
        
        # Обычные пользователи видят только свои задачи
        return RenderTask.objects.filter(user=user).order_by('-started_at')
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'retrieve':
            return RenderTaskDetailSerializer
        return RenderTaskSerializer


class DocumentFilter(filters.FilterSet):
    """Фильтры для документов."""
    
    template = filters.CharFilter(field_name='task__template__name', lookup_expr='icontains')
    format = filters.CharFilter(field_name='task__template__format__name', lookup_expr='icontains')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Document
        fields = ['template', 'format', 'created_after', 'created_before']


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для доступа к сгенерированным документам.
    
    Только чтение, документы создаются задачами рендеринга.
    """
    
    permission_classes = [IsAuthenticated]
    filterset_class = DocumentFilter
    
    def get_queryset(self):
        """Возвращает документы пользователя."""
        user = self.request.user
        
        # Администраторы видят все документы
        if user.is_staff:
            return Document.objects.all().order_by('-created_at')
        
        # Обычные пользователи видят только свои документы
        return Document.objects.filter(task__user=user).order_by('-created_at')
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'retrieve':
            return DocumentDetailSerializer
        return DocumentSerializer