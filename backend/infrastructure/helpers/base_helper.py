"""
Базовый класс хелперов для работы с ресурсами.
"""
import logging
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)


class BaseHelper:
    """
    Базовый класс для всех хелперов.
    
    Предоставляет общие методы и инфраструктуру для хелперов.
    """
    
    @classmethod
    def log_error(cls, message: str, exc: Optional[Exception] = None, level: str = 'error'):
        """
        Унифицированное логирование ошибок.
        
        Args:
            message: Сообщение для логирования
            exc: Исключение (если есть)
            level: Уровень логирования ('error', 'warning', 'info')
        """
        log_message = f"{message}"
        if exc:
            log_message += f": {str(exc)}"
        
        if level == 'error':
            logger.error(log_message)
        elif level == 'warning':
            logger.warning(log_message)
        elif level == 'info':
            logger.info(log_message)
        else:
            logger.debug(log_message)
    
    @classmethod
    def to_dict(cls, obj: Any) -> Dict:
        """
        Преобразует объект в словарь.
        
        Args:
            obj: Объект для преобразования
            
        Returns:
            Dict: Словарь с атрибутами объекта
        """
        if hasattr(obj, '__dict__'):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        else:
            return {}