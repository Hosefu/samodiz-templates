"""
Представления API для работы с шаблонами.
"""
import logging
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import viewsets, mixins, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.templates.models.unit_format import Unit, Format, FormatSetting
from apps.templates.models.template import (
    Template, TemplateRevision, TemplatePermission, 
    Page, PageSettings, Field, Asset
)
from apps.templates.api.serializers import (
    UnitSerializer, FormatSerializer, FormatSettingSerializer, FormatDetailSerializer,
    TemplateListSerializer, TemplateDetailSerializer, TemplateCreateSerializer,
    TemplateRevisionSerializer, TemplatePermissionSerializer,
    PageSerializer, PageSettingsSerializer, FieldSerializer, AssetSerializer
)
from apps.templates.api.permissions import (
    IsTemplateOwnerOrReadOnly, IsTemplateContributor, 
    IsTemplateViewerOrBetter, HasFormatAccess
)
from infrastructure.ceph import ceph_client

logger = logging.getLogger(__name__)


class UnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для работы с единицами измерения.
    
    Только чтение, так как единицы измерения создаются администратором.
    """
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]


class FormatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для работы с форматами документов.
    
    Только чтение, так как форматы создаются администратором.
    """
    queryset = Format.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'retrieve':
            return FormatDetailSerializer
        return FormatSerializer
    
    @action(detail=True, methods=['get'])
    def settings(self, request, pk=None):
        """Получение настроек формата."""
        format_obj = self.get_object()
        settings = format_obj.expected_settings.all()
        serializer = FormatSettingSerializer(settings, many=True)
        return Response(serializer.data)


class TemplateViewSet(viewsets.ModelViewSet):
    """API для работы с шаблонами."""
    
    permission_classes = [IsAuthenticated, IsTemplateOwnerOrReadOnly]
    
    def get_queryset(self):
        """
        Фильтрация шаблонов на основе прав доступа.
        
        Возвращает:
        - Все шаблоны, принадлежащие пользователю
        - Публичные шаблоны
        - Шаблоны, к которым у пользователя есть доступ через permissions
        """
        user = self.request.user
        
        # Администраторы видят все шаблоны
        if user.is_staff:
            return Template.objects.all()
        
        # Обычные пользователи видят свои + доступные им шаблоны
        return Template.objects.filter(
            Q(owner=user) |  # Свои
            Q(is_public=True) |  # Публичные
            Q(permissions__grantee=user)  # Предоставлен доступ
        ).distinct()
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return TemplateCreateSerializer
        if self.action in ['retrieve', 'update', 'partial_update']:
            return TemplateDetailSerializer
        return TemplateListSerializer
    
    def perform_create(self, serializer):
        """Создание нового шаблона."""
        with transaction.atomic():
            # Сохраняем шаблон
            template = serializer.save(owner=self.request.user)
            
            # Создаем первую ревизию шаблона
            TemplateRevision.objects.create(
                template=template,
                number=1,
                author=self.request.user,
                changelog="Первоначальное создание шаблона",
                html=""
            )
            
            # Создаем разрешение владельца
            TemplatePermission.objects.create(
                template=template,
                grantee=self.request.user,
                role='owner'
            )
    
    def perform_update(self, serializer):
        """Обновление шаблона с созданием новой ревизии."""
        with transaction.atomic():
            # Получаем текущую версию
            template = self.get_object()
            latest_revision = template.get_latest_revision()
            
            # Сохраняем шаблон
            updated_template = serializer.save()
            
            # Создаем новую ревизию, если есть изменения
            if latest_revision and 'html' in serializer.initial_data:
                TemplateRevision.objects.create(
                    template=updated_template,
                    number=latest_revision.number + 1,
                    author=self.request.user,
                    changelog=f"Обновление от {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                    html=serializer.initial_data.get('html', latest_revision.html)
                )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsTemplateViewerOrBetter])
    def revisions(self, request, pk=None):
        """Получение истории ревизий шаблона."""
        template = self.get_object()
        revisions = template.revisions.all().order_by('-number')
        serializer = TemplateRevisionSerializer(revisions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsTemplateViewerOrBetter])
    def fields(self, request, pk=None):
        """Получение всех полей шаблона (глобальных и локальных)."""
        template = self.get_object()
        fields = template.fields.all()
        serializer = FieldSerializer(fields, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsTemplateViewerOrBetter])
    def permissions(self, request, pk=None):
        """Получение разрешений шаблона."""
        template = self.get_object()
        permissions = template.permissions.all()
        
        # Пользователи могут видеть только публичные разрешения и свои собственные,
        # владельцы видят все
        if not request.user == template.owner and not request.user.is_staff:
            permissions = permissions.filter(
                Q(grantee=request.user) | Q(grantee__isnull=True)
            )
        
        serializer = TemplatePermissionSerializer(permissions, many=True)
        return Response(serializer.data)


class PageViewSet(viewsets.ModelViewSet):
    """API для работы со страницами шаблона."""
    
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticated, IsTemplateContributor]
    
    def get_queryset(self):
        """Получение страниц определенного шаблона."""
        template_id = self.kwargs.get('template_id')
        return Page.objects.filter(template_id=template_id).order_by('index')
    
    def perform_create(self, serializer):
        """Создание новой страницы с назначением индекса."""
        template_id = self.kwargs.get('template_id')
        template = get_object_or_404(Template, id=template_id)
        
        # Определяем индекс новой страницы
        if 'index' not in serializer.validated_data:
            last_page = template.pages.order_by('-index').first()
            index = 1 if not last_page else last_page.index + 1
            serializer.save(template=template, index=index)
        else:
            serializer.save(template=template)


class FieldViewSet(viewsets.ModelViewSet):
    """API для работы с полями шаблона."""
    
    serializer_class = FieldSerializer
    permission_classes = [IsAuthenticated, IsTemplateContributor]
    
    def get_queryset(self):
        """
        Получение полей определенного шаблона.
        
        Возможна фильтрация по странице или только глобальные поля.
        """
        template_id = self.kwargs.get('template_id')
        page_id = self.request.query_params.get('page_id')
        
        if page_id:
            # Поля конкретной страницы
            return Field.objects.filter(template_id=template_id, page_id=page_id)
        
        # Все поля шаблона
        return Field.objects.filter(template_id=template_id)
    
    def perform_create(self, serializer):
        """Создание нового поля с привязкой к шаблону."""
        template_id = self.kwargs.get('template_id')
        template = get_object_or_404(Template, id=template_id)
        
        # Если указан page_id, проверяем, что страница принадлежит шаблону
        page_id = serializer.validated_data.get('page')
        if page_id and page_id.template.id != template.id:
            return Response(
                {"detail": "Страница не принадлежит этому шаблону."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(template=template)


class AssetViewSet(viewsets.ModelViewSet):
    """API для работы с ассетами шаблона."""
    
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated, IsTemplateContributor]
    
    def get_queryset(self):
        """
        Получение ассетов определенного шаблона.
        
        Возможна фильтрация по странице или только глобальные ассеты.
        """
        template_id = self.kwargs.get('template_id')
        page_id = self.request.query_params.get('page_id')
        
        if page_id:
            # Ассеты конкретной страницы
            return Asset.objects.filter(template_id=template_id, page_id=page_id)
        
        # Все ассеты шаблона
        return Asset.objects.filter(template_id=template_id)
    
    def create(self, request, *args, **kwargs):
        """Загрузка нового ассета."""
        template_id = self.kwargs.get('template_id')
        template = get_object_or_404(Template, id=template_id)
        
        # Проверяем наличие файла в запросе
        if 'file' not in request.FILES:
            return Response(
                {"detail": "Отсутствует файл."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_obj = request.FILES['file']
        page_id = request.data.get('page')
        
        # Проверяем размер файла
        if file_obj.size > settings.MAX_UPLOAD_SIZE:
            return Response(
                {"detail": f"Файл слишком большой. Максимальный размер: {settings.MAX_UPLOAD_SIZE / (1024*1024)} МБ"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Загружаем файл в Ceph
        try:
            folder = f"templates/{template_id}/assets"
            key, url = ceph_client.upload_file(
                file_obj=file_obj,
                folder=folder,
                filename=file_obj.name,
                content_type=file_obj.content_type
            )
            
            # Создаем запись ассета
            asset = Asset.objects.create(
                template=template,
                page_id=page_id if page_id else None,
                name=file_obj.name,
                file=url,
                size_bytes=file_obj.size,
                mime_type=file_obj.content_type
            )
            
            serializer = self.get_serializer(asset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error uploading asset: {e}")
            return Response(
                {"detail": f"Ошибка загрузки файла: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def perform_destroy(self, instance):
        """Удаление ассета с удалением файла из Ceph."""
        try:
            # Извлекаем ключ из URL
            file_key = instance.file.split('/')[-2] + '/' + instance.file.split('/')[-1]
            
            # Удаляем файл из Ceph
            ceph_client.delete_file(file_key)
            
            # Удаляем запись из БД
            instance.delete()
        
        except Exception as e:
            logger.error(f"Error deleting asset: {e}")
            raise


class TemplatePermissionViewSet(viewsets.ModelViewSet):
    """API для работы с разрешениями на доступ к шаблонам."""
    
    serializer_class = TemplatePermissionSerializer
    permission_classes = [IsAuthenticated, IsTemplateContributor]
    
    def get_queryset(self):
        """Получение разрешений определенного шаблона."""
        template_id = self.kwargs.get('template_id')
        return TemplatePermission.objects.filter(template_id=template_id)
    
    def perform_create(self, serializer):
        """Создание нового разрешения с привязкой к шаблону."""
        template_id = self.kwargs.get('template_id')
        template = get_object_or_404(Template, id=template_id)
        serializer.save(template=template)
    
    def destroy(self, request, *args, **kwargs):
        """Удаление разрешения с проверкой прав."""
        permission = self.get_object()
        template = permission.template
        
        # Запрещаем удаление разрешения владельца
        if permission.role == 'owner' and permission.grantee == template.owner:
            return Response(
                {"detail": "Невозможно удалить разрешение владельца."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Только владелец может удалять любые разрешения
        # Редактор может удалять только те разрешения, которые он создал
        if request.user != template.owner and permission.created_by != request.user:
            return Response(
                {"detail": "У вас нет прав на удаление этого разрешения."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)