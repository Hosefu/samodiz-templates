"""
Задачи Celery для очистки старых файлов и удаленных данных.
"""
import logging
from datetime import timedelta
from django.utils import timezone
from celery import shared_task

from apps.generation.models import RenderTask
from apps.templates.models.template import Asset
from infrastructure.ceph import ceph_client

logger = logging.getLogger(__name__)


@shared_task
def cleanup_deleted():
    """
    Физически удаляет файлы, помеченные как удаленные более 30 дней назад.
    
    Этот таск выполняется по расписанию через Celery Beat.
    """
    logger.info("Starting cleanup of deleted files")
    
    # Дата, старше которой удаляем файлы (30 дней назад)
    cutoff_date = timezone.now() - timedelta(days=30)
    
    # Очистка удаленных ассетов
    deleted_assets = Asset.all_objects.filter(
        is_deleted=True,
        deleted_at__lt=cutoff_date
    )
    
    asset_count = 0
    for asset in deleted_assets:
        try:
            # Извлекаем имя объекта из URL
            if 'templates/' in asset.file:
                object_name = asset.file.split('/')[-2] + '/' + asset.file.split('/')[-1]
            else:
                # Для старых файлов
                object_name = asset.file.split('/')[-1]
            
            # Удаляем файл из MinIO
            success = ceph_client.delete_file(object_name)
            
            if success:
                # Физически удаляем запись из БД
                asset.hard_delete()
                asset_count += 1
            else:
                logger.warning(f"Failed to delete asset file from MinIO: {object_name}")
        
        except Exception as e:
            logger.error(f"Error deleting asset {asset.id}: {e}")
    
    logger.info(f"Cleaned up {asset_count} deleted assets")
    
    return {
        'assets_deleted': asset_count,
    }