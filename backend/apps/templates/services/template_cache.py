"""
Сервис кеширования шаблонов.
"""
import json
from typing import Dict, Any, Optional
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from apps.templates.models import Template, FieldVersion


class TemplateCache:
    """Сервис кеширования шаблонов."""
    
    CACHE_TIMEOUT = 3600  # 1 час
    
    @staticmethod
    def get_template_structure(template_id: str, version: Optional[int] = None) -> Dict[str, Any]:
        """
        Получает структуру шаблона из кеша.
        
        Args:
            template_id: ID шаблона
            version: Номер версии (None для текущей)
            
        Returns:
            Dict[str, Any]: Структура шаблона
        """
        cache_key = f"template_structure_{template_id}_{version or 'latest'}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        # Загружаем из БД
        template = Template.objects.select_related(
            'format', 'unit'
        ).prefetch_related(
            'pages__fields', 'fields'
        ).get(id=template_id)
        
        structure = TemplateCache._build_structure(template, version)
        
        # Кешируем
        cache.set(cache_key, json.dumps(structure), TemplateCache.CACHE_TIMEOUT)
        
        return structure
    
    @staticmethod
    def invalidate_template_cache(template_id: str):
        """
        Инвалидирует кеш шаблона.
        
        Args:
            template_id: ID шаблона
        """
        # Получаем все ключи кеша для этого шаблона
        pattern = f"template_structure_{template_id}_*"
        
        # Django не поддерживает wildcard delete, поэтому используем альтернативный подход
        cache.delete_many([
            f"template_structure_{template_id}_latest",
            *[f"template_structure_{template_id}_{i}" for i in range(1, 100)]
        ])
    
    @staticmethod
    def _build_structure(template: Template, version: Optional[int] = None) -> Dict[str, Any]:
        """
        Строит структуру данных для кеша.
        
        Args:
            template: Объект шаблона
            version: Номер версии (None для текущей)
            
        Returns:
            Dict[str, Any]: Структура шаблона
        """
        if version:
            # Получаем структуру из версии
            field_version = FieldVersion.objects.filter(
                template=template,
                version_number=version
            ).first()
            
            if field_version:
                return field_version.fields_snapshot
        
        # Строим текущую структуру
        structure = {
            'id': str(template.id),
            'name': template.name,
            'description': template.description,
            'format': {
                'id': str(template.format.id),
                'name': template.format.name,
            },
            'unit': {
                'id': str(template.unit.id),
                'name': template.unit.name,
                'key': template.unit.key
            },
            'pages': [],
            'global_fields': []
        }
        
        # Добавляем страницы
        for page in template.pages.all().order_by('index'):
            page_data = {
                'id': str(page.id),
                'index': page.index,
                'width': float(page.width),
                'height': float(page.height),
                'fields': []
            }
            
            # Добавляем поля страницы
            for field in page.fields.all().order_by('order'):
                page_data['fields'].append(TemplateCache._serialize_field(field))
            
            structure['pages'].append(page_data)
        
        # Добавляем глобальные поля
        for field in template.fields.filter(page__isnull=True).order_by('order'):
            structure['global_fields'].append(TemplateCache._serialize_field(field))
        
        return structure
    
    @staticmethod
    def _serialize_field(field) -> Dict[str, Any]:
        """Сериализует поле для кеша."""
        field_data = {
            'id': str(field.id),
            'key': field.key,
            'label': field.label,
            'type': field.type,
            'order': field.order,
            'is_required': field.is_required,
            'placeholder': field.placeholder,
            'help_text': field.help_text,
        }
        
        if field.default_value:
            field_data['default_value'] = field.default_value
        
        if field.type == 'choices' and field.choices.exists():
            field_data['choices'] = [
                {
                    'label': choice.label,
                    'value': choice.value,
                    'order': choice.order
                }
                for choice in field.choices.all().order_by('order')
            ]
        
        return field_data 