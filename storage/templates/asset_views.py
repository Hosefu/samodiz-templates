import os
import logging
import magic
from django.conf import settings
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Template, Page, PageAsset
from .permissions import IsOwnerOrHasPermission
from .serializers import PageAssetSerializer

# Настройка логгера
logger = logging.getLogger('template_service')

# Константы для валидации файлов
ALLOWED_MIME_TYPES = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/svg+xml',
    'application/pdf'
]

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_file(file):
    """
    Валидация загружаемого файла
    """
    # Проверка размера
    if file.size > MAX_FILE_SIZE:
        logger.warning(f"File too large: {file.size} bytes")
        return False, f"File size exceeds maximum allowed size of {MAX_FILE_SIZE/1024/1024}MB"

    # Проверка MIME-типа
    mime = magic.Magic(mime=True)
    file_mime = mime.from_buffer(file.read(1024))
    file.seek(0)  # Сброс позиции чтения

    if file_mime not in ALLOWED_MIME_TYPES:
        logger.warning(f"Invalid file type: {file_mime}")
        return False, f"File type {file_mime} is not allowed. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"

    return True, None

@api_view(['POST'])
@parser_classes([MultiPartParser])
@permission_classes([IsOwnerOrHasPermission])
def upload_page_asset(request, template_id, page_id):
    """
    Загрузка ассета для страницы шаблона
    """
    logger.info(f"--- ASSET UPLOAD START ---")
    logger.info(f"Template ID: {template_id}, Page ID: {page_id}")

    try:
        # Проверка наличия файла
        if 'file' not in request.FILES:
            logger.error("No file provided in request")
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получение шаблона и страницы
        template = get_object_or_404(Template, id=template_id)
        page = get_object_or_404(Page, template=template, name=page_id)

        # Проверка прав доступа
        if not template.has_permission(request.user, 'edit'):
            logger.warning(f"User {request.user.id} does not have edit permission for template {template_id}")
            return Response(
                {'error': 'You do not have permission to edit this template'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        file = request.FILES['file']
        logger.info(f"Received file: {file.name}, Size: {file.size} bytes")

        # Валидация файла
        is_valid, error_message = validate_file(file)
        if not is_valid:
            logger.error(f"File validation failed: {error_message}")
            return Response(
                {'error': error_message}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создание ассета
        asset = PageAsset.objects.create(page=page, file=file)
        logger.info(f"Asset created successfully: {asset.id}")

        # Проверка сохранения файла
        if not os.path.exists(asset.file.path):
            logger.error(f"File not found at path: {asset.file.path}")
            asset.delete()
            return Response(
                {'error': 'Error saving file'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Сериализация и возврат результата
        serializer = PageAssetSerializer(asset)
        logger.info(f"--- ASSET UPLOAD END ---")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception(f"Error uploading asset: {str(e)}")
        return Response(
            {'error': f'Error uploading asset: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsOwnerOrHasPermission])
def delete_page_asset(request, template_id, page_id, asset_id):
    """
    Удаление ассета страницы
    """
    logger.info(f"--- ASSET DELETE START ---")
    logger.info(f"Template ID: {template_id}, Page ID: {page_id}, Asset ID: {asset_id}")

    try:
        # Получение шаблона и проверка прав
        template = get_object_or_404(Template, id=template_id)
        if not template.has_permission(request.user, 'edit'):
            logger.warning(f"User {request.user.id} does not have edit permission for template {template_id}")
            return Response(
                {'error': 'You do not have permission to edit this template'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Получение и удаление ассета
        asset = get_object_or_404(
            PageAsset, 
            id=asset_id, 
            page__template=template, 
            page__name=page_id
        )

        # Удаление файла
        file_path = asset.file.path
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File deleted from disk: {file_path}")

        # Удаление записи из БД
        asset.delete()
        logger.info(f"Asset record deleted from database: {asset_id}")

        logger.info(f"--- ASSET DELETE END ---")
        return Response(status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        logger.exception(f"Error deleting asset: {str(e)}")
        return Response(
            {'error': f'Error deleting asset: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 