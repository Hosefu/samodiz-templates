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

from apps.templates.models.template import Template, TemplateRevision
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
    API для генерации документа из шаблона.
    
    Запускает асинхронную задачу рендеринга и возвращает ID задачи.
    """
    
    permission_classes = [IsAuthenticated, IsTemplateViewerOrBetter]
    
    def post(self, request, template_id):
        """Запускает генерацию документа на основе шаблона."""
        # Получаем шаблон
        template = get_object_or_404(Template, id=template_id)
        
        # Проверяем данные запроса
        serializer = GenerateDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                # Получаем последнюю ревизию шаблона
                revision = template.get_latest_revision()
                if not revision:
                    return Response(
                        {"detail": "У шаблона нет ревизий."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Создаем задачу рендеринга
                task = RenderTask.objects.create(
                    template_revision=revision,
                    user=request.user,
                    request_ip=self._get_client_ip(request),
                    data_input=serializer.validated_data,
                    status='pending',
                    progress=0,
                )
                
                # Подготавливаем данные для рендеринга
                data = serializer.validated_data.get('data', {})
                
                # Применяем шаблонизатор к HTML
                try:
                    rendered_html = template_renderer.render_template(revision.html, data)
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
                    'width': float(task.template_revision.template.pages.first().width),
                    'height': float(task.template_revision.template.pages.first().height),
                    'unit': task.template_revision.template.unit.key,
                }
                
                # Добавляем специфичные настройки формата
                format_settings = {}
                for page in task.template_revision.template.pages.all():
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
            logger.error(f"Error starting render task: {e}")
            return Response(
                {"detail": f"Ошибка запуска задачи: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_client_ip(self, request):
        """Получает IP-адрес клиента."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


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
    
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Document
        fields = ['task__template_revision__template', 'created_after', 'created_before']


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