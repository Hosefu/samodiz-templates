from pydantic import BaseModel, Field, field_validator
from typing import Dict, Optional, List, Any, Union


class RenderRequest(BaseModel):
    """
    Модель запроса на рендеринг PNG
    """
    # HTML-содержимое, готовое для рендеринга
    html: str
    
    # Данные для подстановки (опционально)
    data: Optional[Dict[str, str]] = None
    
    # Размеры страницы
    width: int
    height: int
    
    # Единицы измерения (px, mm)
    units: str = "px"
    
    # Дополнительные настройки
    settings: Optional[Dict[str, str]] = None
    
    @field_validator('units')
    def validate_units(cls, v):
        """Проверка корректности единиц измерения"""
        if v.lower() not in ["px", "mm"]:
            raise ValueError("units must be 'px' or 'mm'")
        return v.lower()
    
    @field_validator('width', 'height')
    def validate_dimensions(cls, v):
        """Проверка размеров страницы"""
        if v <= 0:
            raise ValueError("dimensions must be positive")
        return v
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Получение настройки по ключу с значением по умолчанию"""
        if not self.settings:
            return default
        return self.settings.get(key, default)