"""
API представления для генерации документов.
"""
import logging
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status, views, viewsets, generics, permissions
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
from apps.generation.models import RenderTask, GeneratedDocument
from apps.generation.api.serializers import (
    RenderTaskSerializer, RenderTaskDetailSerializer,
    DocumentSerializer, DocumentDetailSerializer,
    GenerateDocumentSerializer,
    TemplateSerializer
)
from apps.generation.tasks.render import render_pdf, render_png, render_svg
from apps.generation.services.document_generation_service import DocumentGenerationService, DocumentGenerationError

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


class TemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с шаблонами документов.
    """
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Возвращает только шаблоны пользователя."""
        return self.queryset.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        """Создает шаблон с привязкой к пользователю."""
        serializer.save(owner=self.request.user)


class RenderTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра задач рендеринга.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Возвращает задачи пользователя."""
        user = self.request.user
        
        if user.is_staff:
            return RenderTask.objects.all().order_by('-started_at')
        
        return RenderTask.objects.filter(user=user).order_by('-started_at')
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'retrieve':
            return RenderTaskDetailSerializer
        return RenderTaskSerializer


class DocumentFilter(filters.FilterSet):
    """Фильтры для документов."""
    
    template = filters.CharFilter(field_name='task__template__name', lookup_expr='icontains')
    format = filters.CharFilter(field_name='task__template__format__name', lookup_expr='iexact')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = GeneratedDocument
        fields = ['template', 'format', 'created_after', 'created_before']


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра документов.
    """
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = DocumentFilter
    
    def get_queryset(self):
        """Возвращает документы пользователя."""
        user = self.request.user
        
        if user.is_staff:
            return GeneratedDocument.objects.all().order_by('-created_at')
        
        return GeneratedDocument.objects.filter(task__user=user).order_by('-created_at')
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'retrieve':
            return DocumentDetailSerializer
        return DocumentSerializer


class GenerateDocumentViewSet(viewsets.GenericViewSet):
    """
    ViewSet для генерации документов.
    """
    permission_classes = [IsPublicTemplateOrAuthenticated]
    serializer_class = GenerateDocumentSerializer
    
    def get_object(self):
        """Получает шаблон по ID."""
        template_id = self.kwargs.get('template_id')
        return get_object_or_404(Template, id=template_id)
    
    def generate(self, request, template_id=None):
        """
        Генерирует документ из шаблона.
        """
        template = self.get_object()
        
        # Проверяем права доступа
        self.check_object_permissions(request, template)
        
        # Валидируем данные
        serializer = self.get_serializer(data=request.data, context={'template': template})
        serializer.is_valid(raise_exception=True)
        
        try:
            # Генерируем документ
            task = DocumentGenerationService.generate_document(
                template=template,
                data=serializer.validated_data['data'],
                user=request.user,
                request_ip=self._get_client_ip(request)
            )
            
            # Возвращаем информацию о задаче
            return Response(
                RenderTaskSerializer(task).data,
                status=status.HTTP_202_ACCEPTED
            )
            
        except DocumentGenerationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in document generation: {e}")
            return Response(
                {'error': 'Произошла неожиданная ошибка'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='fields')
    def get_template_fields(self, request, template_id=None):
        """Возвращает структуру полей шаблона для генерации."""
        template = self.get_object()
        
        # Собираем структуру полей
        global_fields = []
        page_fields = {}
        
        for field in template.fields.all().order_by('page__index', 'order'):
            field_info = {
                'key': field.key,
                'label': field.label,
                'type': field.type,
                'required': field.is_required,
                'placeholder': field.placeholder,
                'help_text': field.help_text,
            }
            
            if field.default_value:
                field_info['default_value'] = field.default_value
            
            if field.type == 'choices' and field.choices.exists():
                field_info['choices'] = [
                    {'label': choice.label, 'value': choice.value}
                    for choice in field.choices.all().order_by('order')
                ]
            
            if field.page is None:
                global_fields.append(field_info)
            else:
                page_key = str(field.page.index)
                if page_key not in page_fields:
                    page_fields[page_key] = []
                page_fields[page_key].append(field_info)
        
        return Response({
            'global_fields': global_fields,
            'page_fields': page_fields
        })
    
    def _get_client_ip(self, request):
        """Получает IP адрес клиента."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
