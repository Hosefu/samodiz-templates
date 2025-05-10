"""
API представления для генерации документов.
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
from apps.generation.models import RenderTask, GeneratedDocument
from apps.generation.api.serializers import (
    RenderTaskSerializer, RenderTaskDetailSerializer,
    DocumentSerializer, DocumentDetailSerializer,
    GenerateDocumentSerializer,
    TemplateSerializer
)
from apps.generation.tasks.render import render_pdf, render_png, render_svg
from apps.generation.services.document_generation_service import DocumentGenerationService

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
    serializer_class = RenderTaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Возвращает только задачи пользователя."""
        return RenderTask.objects.filter(template__owner=self.request.user)


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра сгенерированных документов.
    """
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Возвращает только документы пользователя."""
        return GeneratedDocument.objects.filter(task__template__owner=self.request.user)


class GenerateDocumentView(viewsets.ViewSet):
    """
    ViewSet для генерации документов из шаблонов.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, template_id):
        """
        Генерирует документ из шаблона.
        
        Args:
            request: HTTP запрос
            template_id: ID шаблона
            
        Returns:
            Response с информацией о задаче рендеринга
        """
        # Получаем шаблон
        template = get_object_or_404(Template, id=template_id, owner=request.user)
        
        # Валидируем входные данные
        serializer = GenerateDocumentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Генерируем документ через сервис
            document_id = DocumentGenerationService.generate_document(
                template=template,
                format_type=serializer.validated_data['format'],
                data=serializer.validated_data.get('data', {}),
                user=request.user
            )
            
            # Получаем задачу рендеринга
            render_task = RenderTask.objects.get(documents__id=document_id)
            
            return Response(
                RenderTaskSerializer(render_task).data,
                status=status.HTTP_202_ACCEPTED
            )
            
        except Exception as e:
            logger.error(f"Error generating document: {e}")
            return Response(
                {'error': str(e)},
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

class DocumentFilter(filters.FilterSet):
    """Фильтры для документов."""
    
    template = filters.CharFilter(field_name='task__template__name', lookup_expr='icontains')
    format = filters.CharFilter(field_name='task__template__format__name', lookup_expr='icontains')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = GeneratedDocument
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
            return GeneratedDocument.objects.all().order_by('-created_at')
        
        # Обычные пользователи видят только свои документы
        return GeneratedDocument.objects.filter(task__user=user).order_by('-created_at')
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'retrieve':
            return DocumentDetailSerializer
        return DocumentSerializer
