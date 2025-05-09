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
from apps.templates.api.permissions import IsTemplateViewerOrBetter
from apps.templates.services.templating import template_renderer
from apps.generation.models import RenderTask, Document
from apps.generation.api.serializers import (
    RenderTaskSerializer, RenderTaskDetailSerializer,
    DocumentSerializer, DocumentDetailSerializer,
    GenerateDocumentSerializer
)
from apps.generation.tasks.render import render_pdf, render_png, render_svg

logger = logging.getLogger(__name__)


class GenerateDocumentView(views.APIView):
    """
    API для генерации документов на основе шаблонов.
    
    Принимает данные для подстановки в шаблон и запускает асинхронную задачу рендеринга.
    """
    permission_classes = [IsAuthenticated, IsTemplateViewerOrBetter]
    
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
                        revisions.set_user(request.user)
                        revisions.set_comment("Auto-created during document generation")
                        current_version = Version.objects.get_for_object(template).first()
                
                # Создаем задачу рендеринга
                task = RenderTask.objects.create(
                    template=template,
                    version_id=current_version.id,
                    user=request.user,
                    request_ip=self._get_client_ip(request),
                    data_input=serializer.validated_data,
                    status='pending',
                    progress=0,
                )
                
                # Подготавливаем данные для рендеринга
                data = serializer.validated_data.get('data', {})
                
                # Применяем шаблонизатор к HTML, используя версию из reversion
                try:
                    template_html = current_version.field_dict.get('html', template.html)
                    rendered_html = template_renderer.render_template(template_html, data)
                except Exception as e:
                    logger.error(f"Template rendering error: {e}")
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
                options = {
                    # Базовые опции
                    'format': format_name,
                    'width': float(template.pages.first().width),
                    'height': float(template.pages.first().height),
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
        """Возвращает список полей шаблона для генерации документа."""
        template = get_object_or_404(Template, id=template_id)
        self.check_object_permissions(request, template)
        
        fields = template.fields.all().order_by('page', 'key')
        
        # Формируем список полей с метаданными
        field_data = []
        for field in fields:
            field_info = {
                'key': field.key,
                'label': field.label,
                'required': field.is_required,
                'page': field.page.index if field.page else None,
                'is_global': field.page is None,
            }
            
            if field.default_value:
                field_info['default_value'] = field.default_value
                
            if field.is_choices:
                field_info['choices'] = field.choices
                
            field_data.append(field_info)
        
        return Response(field_data)


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