"""
Импорты моделей для приложения шаблонов.
"""
# Сначала импортируем базовые модели
from apps.templates.models.unit_format import Unit, Format, FormatSetting

# Затем модели, которые зависят от базовых
from apps.templates.models.template import (
    Template, 
    Page, 
    TemplatePermission, 
    PageSettings, 
    Field, 
    FieldChoice,
    Asset, 
    FieldVersion
)

# Делаем все доступным на уровне пакета
__all__ = [
    'Unit', 'Format', 'FormatSetting',
    'Template', 'Page', 'TemplatePermission', 'PageSettings',
    'Field', 'FieldChoice', 'Asset', 'FieldVersion'
] 