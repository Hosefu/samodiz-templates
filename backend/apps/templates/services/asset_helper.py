"""
Хелпер для работы с ассетами шаблонов.
"""
import logging
from typing import Optional, List, Dict, BinaryIO, Union, Tuple
from pathlib import Path
from io import BytesIO
from django.conf import settings
from apps.templates.models.template import Asset, Template
from infrastructure.minio_client import minio_client

logger = logging.getLogger(__name__)


class AssetHelper:
    """Централизованный сервис для управления ассетами."""
    
    # Маппинг MIME-типов по расширениям
    MIME_TYPES = {
        '.ttf': 'font/ttf',
        '.otf': 'font/otf',
        '.woff': 'font/woff',
        '.woff2': 'font/woff2',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
        '.pdf': 'application/pdf',
    }
    
    @classmethod
    def upload_asset(
        cls,
        template_id: str,
        file_obj: Union[BinaryIO, Path, str],
        filename: Optional[str] = None,
        page_id: Optional[str] = None,
        mime_type: Optional[str] = None
    ) -> Asset:
        """
        Загружает ассет в MinIO и создает запись в БД.
        
        Args:
            template_id: ID шаблона
            file_obj: Файловый объект, путь к файлу или bytes
            filename: Имя файла (автоматически определяется если не указано)
            page_id: ID страницы (None для глобального ассета)
            mime_type: MIME-тип (автоматически определяется если не указано)
            
        Returns:
            Asset: Созданный объект ассета
            
        Raises:
            ValueError: Если шаблон не найден
            FileNotFoundError: Если файл не найден
            ValueError: Если не удалось определить имя файла
        """
        # Получаем шаблон
        try:
            template = Template.objects.get(id=template_id)
        except Template.DoesNotExist:
            raise ValueError(f"Template not found: {template_id}")
        
        # Преобразуем различные типы входных данных в BytesIO
        if isinstance(file_obj, (str, Path)):
            # Если передан путь к файлу
            file_path = Path(file_obj)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            filename = filename or file_path.name
            with open(file_path, 'rb') as f:
                file_content = f.read()
            file_obj = BytesIO(file_content)
            
        elif isinstance(file_obj, bytes):
            # Если переданы raw bytes
            file_obj = BytesIO(file_obj)
            if not filename:
                raise ValueError("filename must be provided when uploading raw bytes")
        
        elif hasattr(file_obj, 'read'):
            # Если это уже файловый объект
            if hasattr(file_obj, 'name') and not filename:
                filename = Path(file_obj.name).name
        
        else:
            raise ValueError(f"Unsupported file_obj type: {type(file_obj)}")
        
        # Определяем MIME-тип если не указан
        if mime_type is None and filename:
            ext = Path(filename).suffix.lower()
            mime_type = cls.MIME_TYPES.get(ext, 'application/octet-stream')
        
        # Определяем размер файла
        current_pos = file_obj.tell() if hasattr(file_obj, 'tell') else 0
        file_obj.seek(0, 2)  # Seek to end
        file_size = file_obj.tell()
        file_obj.seek(current_pos)  # Return to original position
        
        # Определяем папку для сохранения
        if page_id:
            folder = f"templates/{template_id}/assets/pages/{page_id}"
        else:
            folder = f"templates/{template_id}/assets/global"
        
        # Загружаем файл в MinIO
        try:
            object_name, public_url = minio_client.upload_file(
                file_obj=file_obj,
                folder=folder,
                filename=filename,
                content_type=mime_type,
                bucket_type='templates'
            )
        except Exception as e:
            logger.error(f"Failed to upload asset to MinIO: {e}")
            raise
        
        # Создаем запись в БД
        asset = Asset.objects.create(
            template=template,
            page_id=page_id,
            name=filename,
            file=public_url,
            size_bytes=file_size,
            mime_type=mime_type
        )
        
        logger.info(f"Asset uploaded: {filename} ({file_size} bytes) to {object_name}")
        return asset
    
    @classmethod
    def delete_asset(cls, asset: Union[Asset, str]) -> bool:
        """
        Удаляет ассет из MinIO и БД.
        
        Args:
            asset: Объект Asset или его ID
            
        Returns:
            bool: True если успешно удален
        """
        # Получаем объект Asset если передан ID
        if isinstance(asset, str):
            try:
                asset = Asset.objects.get(id=asset)
            except Asset.DoesNotExist:
                logger.error(f"Asset not found: {asset}")
                return False
        
        try:
            # Парсим URL для получения имени объекта
            from urllib.parse import urlparse
            parsed_url = urlparse(asset.file)
            path_parts = parsed_url.path.strip('/').split('/')
            
            # Извлекаем object_name (все после bucket)
            if len(path_parts) >= 2:
                object_name = '/'.join(path_parts[1:])
            else:
                logger.error(f"Invalid asset URL: {asset.file}")
                return False
            
            # Удаляем файл из MinIO
            success = minio_client.delete_file(object_name, 'templates')
            
            if success:
                # Удаляем запись из БД
                asset.delete()
                logger.info(f"Asset deleted: {asset.name}")
                return True
            else:
                logger.error(f"Failed to delete asset from MinIO: {object_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting asset {asset.id}: {e}")
            return False
    
    @classmethod
    def get_asset_metadata(cls, asset_id: str) -> Optional[Dict]:
        """
        Получает метаданные ассета.
        
        Args:
            asset_id: ID ассета
            
        Returns:
            Optional[Dict]: Метаданные ассета или None
        """
        try:
            asset = Asset.objects.get(id=asset_id)
            return {
                'id': str(asset.id),
                'name': asset.name,
                'size': asset.size_bytes,
                'mime_type': asset.mime_type,
                'url': cls.get_asset_url(str(asset.template.id), asset.name, str(asset.page.id) if asset.page else None),
                'template_id': str(asset.template.id),
                'page_id': str(asset.page.id) if asset.page else None,
                'created_at': asset.created_at.isoformat(),
                'updated_at': asset.updated_at.isoformat(),
            }
        except Asset.DoesNotExist:
            return None
    
    @staticmethod
    def find_asset(template_id: str, asset_name: str, page_id: Optional[str] = None) -> Optional[Asset]:
        """
        Находит ассет по имени с учетом приоритета поиска.
        
        Args:
            template_id: ID шаблона
            asset_name: Имя ассета
            page_id: (optional) ID страницы для поиска локальных ассетов
            
        Returns:
            Asset или None, если не найден
        """
        try:
            template = Template.objects.get(id=template_id)
        except Template.DoesNotExist:
            logger.error(f"Template not found: {template_id}")
            return None
        
        # Если указана страница, сначала ищем среди ее ассетов
        if page_id:
            page_asset = Asset.objects.filter(
                template=template,
                page_id=page_id,
                name=asset_name
            ).first()
            
            if page_asset:
                return page_asset
        
        # Ищем среди глобальных ассетов
        global_asset = Asset.objects.filter(
            template=template,
            page__isnull=True,
            name=asset_name
        ).first()
        
        return global_asset
    
    @staticmethod
    def get_asset_url(template_id: str, asset_name: str, page_id: Optional[str] = None) -> str:
        """
        Получает подписанный URL ассета.
        
        Args:
            template_id: ID шаблона
            asset_name: Имя ассета
            page_id: (optional) ID страницы для поиска локальных ассетов
            
        Returns:
            URL ассета или пустую строку, если не найден
        """
        asset = AssetHelper.find_asset(template_id, asset_name, page_id)
        if asset and asset.file:
            from urllib.parse import urlparse
            from datetime import timedelta
            
            # Парсим сохранённый URL
            parsed_url = urlparse(asset.file)
            path_parts = parsed_url.path.strip('/').split('/')
            
            if len(path_parts) >= 2:
                object_name = '/'.join(path_parts[1:])
                # Генерируем подписанную ссылку на 24 часа
                return minio_client.get_presigned_url(object_name, 'templates', timedelta(hours=24))
            else:
                logger.error(f"Invalid asset URL: {asset.file}")
                return ""
        
        logger.warning(f"Asset not found: {asset_name} in template {template_id}")
        return ""
    
    @staticmethod
    def list_template_assets(template_id: str, include_page_assets: bool = True) -> Dict[str, List[Dict]]:
        """
        Получает список всех ассетов шаблона.
        
        Args:
            template_id: ID шаблона
            include_page_assets: Включать ли ассеты страниц
            
        Returns:
            Словарь с глобальными и постраничными ассетами
        """
        try:
            template = Template.objects.get(id=template_id)
        except Template.DoesNotExist:
            logger.error(f"Template not found: {template_id}")
            return {"global": [], "pages": {}}
        
        result = {
            "global": [],
            "pages": {}
        }
        
        # Получаем глобальные ассеты
        global_assets = Asset.objects.filter(
            template=template,
            page__isnull=True
        ).order_by('name')
        
        for asset in global_assets:
            result["global"].append({
                "id": str(asset.id),
                "name": asset.name,
                "url": asset.file,
                "size": asset.size_bytes,
                "mime_type": asset.mime_type
            })
        
        # Получаем ассеты страниц
        if include_page_assets:
            page_assets = Asset.objects.filter(
                template=template,
                page__isnull=False
            ).order_by('page__index', 'name')
            
            for asset in page_assets:
                page_key = str(asset.page.index)
                if page_key not in result["pages"]:
                    result["pages"][page_key] = []
                
                result["pages"][page_key].append({
                    "id": str(asset.id),
                    "name": asset.name,
                    "url": asset.file,
                    "size": asset.size_bytes,
                    "mime_type": asset.mime_type
                })
        
        return result


# Создаем глобальный инстанс
asset_helper = AssetHelper() 