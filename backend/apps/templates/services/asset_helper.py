"""
Хелпер для работы с ассетами шаблонов.
"""
import logging
from typing import Optional, List, Dict
from apps.templates.models.template import Asset, Template

logger = logging.getLogger(__name__)


class AssetHelper:
    """Хелпер для управления ассетами."""
    
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
        Получает URL ассета.
        
        Args:
            template_id: ID шаблона
            asset_name: Имя ассета
            page_id: (optional) ID страницы для поиска локальных ассетов
            
        Returns:
            URL ассета или пустую строку, если не найден
        """
        asset = AssetHelper.find_asset(template_id, asset_name, page_id)
        if asset and asset.file:
            # Проверяем права доступа к шаблону
            template = asset.template
            if template.is_public:
                # Для публичных шаблонов возвращаем прямую ссылку
                return asset.file
            else:
                # Для приватных шаблонов генерируем подписанную ссылку
                object_name = asset.file.split('/')[-1]  # Извлекаем имя объекта
                folder = f"templates/{template_id}/assets"
                if asset.page:
                    folder = f"templates/{template_id}/assets/pages/{asset.page.id}"
                else:
                    folder = f"templates/{template_id}/assets/global"
                
                from infrastructure.minio_client import minio_client
                return minio_client.get_presigned_url(f"{folder}/{object_name}", 'templates')
        
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
                    "name": asset.name,
                    "url": asset.file,
                    "size": asset.size_bytes,
                    "mime_type": asset.mime_type
                })
        
        return result


# Создаем глобальный инстанс
asset_helper = AssetHelper() 