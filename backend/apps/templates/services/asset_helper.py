"""
Хелпер для работы с ассетами шаблонов.
"""
import logging
from typing import Optional, List, Dict, BinaryIO, Union
from pathlib import Path
from io import BytesIO
from django.conf import settings
from apps.templates.models.template import Asset, Template
from infrastructure.helpers.file_helper import FileHelper

logger = logging.getLogger(__name__)


class AssetHelper(FileHelper):
    """Централизованный сервис для управления ассетами шаблонов."""
    
    @classmethod
    def upload_asset(
        cls,
        template_id: str,
        file_obj: Union[BinaryIO, Path, str, bytes],
        filename: Optional[str] = None,
        page_id: Optional[str] = None,
        mime_type: Optional[str] = None
    ) -> Asset:
        """
        Загружает ассет в хранилище и создает запись в БД.
        
        Args:
            template_id: ID шаблона
            file_obj: Файловый объект, путь к файлу или байты
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
        
        # Подготавливаем файловый объект и получаем его размер
        if isinstance(file_obj, (str, Path)):
            file_path = Path(file_obj)
            file_size = file_path.stat().st_size
        elif isinstance(file_obj, bytes):
            file_size = len(file_obj)
        elif hasattr(file_obj, 'getbuffer'):
            file_size = len(file_obj.getbuffer())
        elif hasattr(file_obj, 'size'):
            file_size = file_obj.size
        else:
            # Если не можем определить размер
            current_pos = file_obj.tell() if hasattr(file_obj, 'tell') else 0
            file_obj.seek(0, 2)  # Seek to end
            file_size = file_obj.tell()
            file_obj.seek(current_pos)  # Return to original position
        
        # Определяем папку для сохранения
        if page_id:
            folder = f"templates/{template_id}/assets/pages/{page_id}"
        else:
            folder = f"templates/{template_id}/assets/global"
        
        # Загружаем файл в хранилище
        try:
            object_name, public_url = cls.upload_file(
                file_obj=file_obj,
                folder=folder,
                filename=filename,
                mime_type=mime_type,
                bucket_type='templates'
            )
        except Exception as e:
            cls.log_error(f"Failed to upload asset to storage", e)
            raise
        
        # Создаем запись в БД
        asset = Asset.objects.create(
            template=template,
            page_id=page_id,
            name=filename,
            file=public_url,
            size_bytes=file_size,
            mime_type=mime_type or cls._get_mime_type(Path(filename).suffix.lower())
        )
        
        logger.info(f"Asset uploaded: {filename} ({file_size} bytes) to {object_name}")
        return asset
    
    @classmethod
    def delete_asset(cls, asset: Union[Asset, str]) -> bool:
        """
        Удаляет ассет из хранилища и БД.
        
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
                cls.log_error(f"Asset not found: {asset}", level='warning')
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
                cls.log_error(f"Invalid asset URL: {asset.file}", level='warning')
                return False
            
            # Удаляем файл из хранилища
            success = cls.delete_file(object_name, 'templates')
            
            if success:
                # Удаляем запись из БД
                asset.delete()
                logger.info(f"Asset deleted: {asset.name}")
                return True
            else:
                cls.log_error(f"Failed to delete asset from storage: {object_name}", level='warning')
                return False
                
        except Exception as e:
            cls.log_error(f"Error deleting asset {asset.id}", e)
            return False
    
    @classmethod
    def get_asset_url(cls, template_id: str, asset_name: str, page_id: Optional[str] = None) -> str:
        """
        Получает подписанный URL ассета.
        
        Args:
            template_id: ID шаблона
            asset_name: Имя ассета
            page_id: (optional) ID страницы для поиска локальных ассетов
            
        Returns:
            str: URL ассета или пустую строку, если не найден
        """
        asset = cls.find_asset(template_id, asset_name, page_id)
        if asset and asset.file:
            # Используем метод базового класса
            return cls.get_presigned_url(asset.file, 'templates')
        
        cls.log_error(f"Asset not found: {asset_name} in template {template_id}", level='warning')
        return ""
    
    @classmethod
    def list_template_assets(cls, template_id: str, include_page_assets: bool = True) -> Dict[str, List[Dict]]:
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
            cls.log_error(f"Template not found: {template_id}", level='warning')
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
                "url": cls.get_presigned_url(asset.file, 'templates'),
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
                    "url": cls.get_presigned_url(asset.file, 'templates'),
                    "size": asset.size_bytes,
                    "mime_type": asset.mime_type
                })
        
        return result
    
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


# Создаем глобальный инстанс
asset_helper = AssetHelper() 