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
from reversion.models import Version
from reversion.views import RevisionMixin
from reversion import revisions

from apps.templates.models.unit_format import Unit, Format, FormatSetting
from apps.templates.models.template import (
    Template, TemplatePermission, 
    Page, PageSettings, Field, Asset, FieldChoice
)
from apps.templates.api.serializers import (
    UnitSerializer, FormatSerializer, FormatSettingSerializer, FormatDetailSerializer,
    TemplateListSerializer, TemplateDetailSerializer, TemplateCreateSerializer,
    TemplateVersionSerializer, TemplatePermissionSerializer,
    PageSerializer, PageSettingsSerializer, FieldSerializer, AssetSerializer,
    VersionSerializer, FieldChoiceSerializer
)
from apps.templates.api.permissions import (
    IsTemplateOwnerOrReadOnly, IsTemplateContributor, 
    IsTemplateViewerOrBetter, HasFormatAccess
)
from apps.templates.services.template_version_service import template_version_service
from infrastructure.minio_client import minio_client

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
    def get_format_settings(self, request, pk=None):
        """Получение настроек формата."""
        format_obj = self.get_object()
        settings_data = format_obj.expected_settings.all()
        serializer = FormatSettingSerializer(settings_data, many=True)
        return Response(serializer.data)


class TemplateViewSet(RevisionMixin, viewsets.ModelViewSet):
    """API для работы с шаблонами."""
    
    permission_classes = [IsTemplateOwnerOrReadOnly]
    
    def get_queryset(self):
        """Получение списка шаблонов с учетом прав доступа."""
        user = self.request.user
        
        if not user.is_authenticated:
            # Анонимные пользователи видят только публичные шаблоны
            return Template.objects.filter(is_public=True)
        
        if user.is_staff:
            # Администраторы видят все шаблоны
            return Template.objects.all()
        
        # Обычные пользователи видят свои шаблоны и те, к которым имеют доступ
        return Template.objects.filter(
            Q(owner=user) |  # Владелец
            Q(is_public=True) |  # Публичные шаблоны
            Q(permissions__grantee=user)  # Шаблоны с доступом
        ).distinct()
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return TemplateCreateSerializer
        if self.action in ['retrieve', 'update', 'partial_update']:
            return TemplateDetailSerializer
        return TemplateListSerializer
    
    def perform_create(self, serializer):
        """Создание нового шаблона с версией."""
        with transaction.atomic():
            with revisions.create_revision():
                # Сохраняем шаблон
                template = serializer.save(owner=self.request.user)
                revisions.set_user(self.request.user)
                revisions.set_comment("Initial version")
                
                # Создаем разрешение владельца
                TemplatePermission.objects.create(
                    template=template,
                    grantee=self.request.user,
                    role='owner'
                )
    
    def perform_update(self, serializer):
        """Обновление шаблона с созданием новой версии."""
        with transaction.atomic():
            with revisions.create_revision():
                template = serializer.save()
                revisions.set_user(self.request.user)
                revisions.set_comment(f"Update from {timezone.now().strftime('%Y-%m-%d %H:%M')}")
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsTemplateViewerOrBetter])
    def versions(self, request, pk=None):
        """Получение истории версий шаблона."""
        template = self.get_object()
        versions = Version.objects.get_for_object(template).order_by('-revision__date_created')
        
        versions_data = []
        for i, version in enumerate(versions):
            versions_data.append({
                'id': version.id,
                'version_number': i + 1,  # Порядковый номер версии
                'date_created': version.revision.date_created,
                'user': {
                    'id': str(version.revision.user.id) if version.revision.user else None,
                    'email': version.revision.user.email if version.revision.user else None,
                    'full_name': version.revision.user.get_full_name() if version.revision.user else None,
                },
                'comment': version.revision.comment,
            })
        
        return Response(versions_data)
    
    @action(detail=True, methods=['get'], url_path=r'versions/(?P<version_id>\d+)')
    def get_version(self, request, pk=None, version_id=None):
        """Получение конкретной версии шаблона."""
        template = self.get_object()
        
        try:
            version = Version.objects.get_for_object(template).get(id=version_id)
            template_data = version.field_dict
            
            # Добавляем метаданные
            template_data['version_id'] = version.id
            template_data['date_created'] = version.revision.date_created
            template_data['user'] = {
                'id': str(version.revision.user.id) if version.revision.user else None,
                'email': version.revision.user.email if version.revision.user else None,
                'full_name': version.revision.user.get_full_name() if version.revision.user else None,
            }
            template_data['comment'] = version.revision.comment
            
            return Response(template_data)
        except Version.DoesNotExist:
            return Response({'error': 'Version not found'}, status=404)
    
    @action(detail=True, methods=['post'], url_path=r'versions/(?P<version_id>\d+)/revert')
    def revert_to_version(self, request, pk=None, version_id=None):
        """Откат шаблона к указанной версии."""
        template = self.get_object()
        
        try:
            version = Version.objects.get_for_object(template).get(id=version_id)
            
            with transaction.atomic():
                with revisions.create_revision():
                    version.revision.revert()
                    
                    # Обновляем объект после отката
                    template.refresh_from_db()
                    
                    revisions.set_user(request.user)
                    revisions.set_comment(f"Reverted to version from {version.revision.date_created}")
                    
                    # Необходимо явно сохранить, чтобы создать новую версию
                    template.save()
                    
                    return Response({'status': 'reverted'})
        except Version.DoesNotExist:
            return Response({'error': 'Version not found'}, status=404)
    
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

    @action(detail=True, methods=['get'])
    def fields_for_generation(self, request, pk=None):
        """Получение полей для генерации документа."""
        template = self.get_object()
        fields = template.fields.all().order_by('page', 'order')
        return Response(FieldSerializer(fields, many=True).data)


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
        
        # Загружаем файл в MinIO
        try:
            folder = f"templates/{template_id}/assets"
            object_name, url = minio_client.upload_file(
                file_obj=file_obj,
                folder=folder,
                filename=file_obj.name,
                content_type=file_obj.content_type,
                bucket_type='templates'
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
        """Удаление ассета с удалением файла из MinIO."""
        try:
            # Извлекаем имя объекта из URL
            object_name = '/'.join(instance.file.split('/')[-3:])  # Берем последние 3 части пути
            
            # Удаляем файл из MinIO
            minio_client.delete_file(object_name, 'templates')
            
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


class FieldChoiceViewSet(viewsets.ModelViewSet):
    """API для работы с вариантами выбора поля."""
    
    serializer_class = FieldChoiceSerializer
    permission_classes = [IsAuthenticated, IsTemplateOwnerOrReadOnly]
    
    def get_queryset(self):
        """Получение вариантов выбора определенного поля."""
        field_id = self.kwargs.get('field_id')
        return FieldChoice.objects.filter(field_id=field_id).order_by('order')
    
    def perform_create(self, serializer):
        """Создание нового варианта выбора."""
        field_id = self.kwargs.get('field_id')
        field = get_object_or_404(Field, id=field_id)
        
        # Проверяем, что поле имеет тип choices
        if field.type != 'choices':
            return Response(
                {"detail": "Варианты выбора можно добавлять только для полей типа choices."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Определяем порядок нового варианта
        if 'order' not in serializer.validated_data:
            last_choice = field.choices.order_by('-order').first()
            order = 1 if not last_choice else last_choice.order + 1
            serializer.save(field=field, order=order)
        else:
            serializer.save(field=field)