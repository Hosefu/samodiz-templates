import os
import hashlib
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from loguru import logger

from app.config import settings


class TemplateCache:
    """
    Сервис для кэширования HTML-шаблонов и результатов рендеринга
    """
    
    def __init__(self):
        """Инициализация кэша шаблонов"""
        self.cache_dir = settings.CACHE_DIR
        self.enabled = settings.CACHE_ENABLED
        self.expiration = settings.CACHE_EXPIRATION
        
        # Создаем директорию для кэша, если она не существует
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def get_cache_key(self, html: str, width: int, height: int, units: str, 
                      settings_dict: Optional[Dict[str, str]] = None) -> str:
        """
        Генерирует ключ кэша на основе параметров рендеринга
        
        Args:
            html: HTML-содержимое
            width: Ширина
            height: Высота
            units: Единицы измерения
            settings_dict: Дополнительные настройки
            
        Returns:
            str: Хеш-ключ для кэша
        """
        # Формируем словарь параметров
        params = {
            "width": width,
            "height": height,
            "units": units,
        }
        
        # Добавляем настройки, если они есть
        if settings_dict:
            params["settings"] = settings_dict
        
        # Сериализуем параметры
        params_str = json.dumps(params, sort_keys=True)
        
        # Создаем хеш-ключ из HTML и параметров
        key = hashlib.sha256()
        key.update(html.encode('utf-8'))
        key.update(params_str.encode('utf-8'))
        
        return key.hexdigest()
    
    def get_from_cache(self, cache_key: str) -> Optional[bytes]:
        """
        Получает результат рендеринга из кэша
        
        Args:
            cache_key: Ключ кэша
            
        Returns:
            Optional[bytes]: Данные изображения или None, если кэш не найден
        """
        if not self.enabled:
            return None
        
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.png")
        meta_file = os.path.join(self.cache_dir, f"{cache_key}.meta")
        
        # Проверяем наличие файлов
        if not os.path.exists(cache_file) or not os.path.exists(meta_file):
            return None
        
        try:
            # Проверяем метаданные и срок действия кэша
            with open(meta_file, 'r') as f:
                meta = json.load(f)
                
            # Проверяем срок действия кэша
            if time.time() - meta.get('timestamp', 0) > self.expiration:
                logger.info(f"Cache expired for key: {cache_key}")
                # Удаляем устаревшие файлы
                os.remove(cache_file)
                os.remove(meta_file)
                return None
            
            # Читаем данные изображения
            with open(cache_file, 'rb') as f:
                image_data = f.read()
                
            logger.info(f"Cache hit for key: {cache_key}")
            return image_data
            
        except Exception as e:
            logger.error(f"Error reading from cache: {str(e)}")
            return None
    
    def save_to_cache(self, cache_key: str, image_data: bytes, 
                      metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Сохраняет результат рендеринга в кэш
        
        Args:
            cache_key: Ключ кэша
            image_data: Данные изображения
            metadata: Дополнительные метаданные
            
        Returns:
            bool: True, если сохранение прошло успешно
        """
        if not self.enabled:
            return False
        
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.png")
        meta_file = os.path.join(self.cache_dir, f"{cache_key}.meta")
        
        try:
            # Сохраняем данные изображения
            with open(cache_file, 'wb') as f:
                f.write(image_data)
            
            # Сохраняем метаданные
            meta = {
                'timestamp': time.time(),
                'size': len(image_data)
            }
            
            # Добавляем дополнительные метаданные, если они есть
            if metadata:
                meta.update(metadata)
            
            with open(meta_file, 'w') as f:
                json.dump(meta, f)
                
            logger.info(f"Saved to cache: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to cache: {str(e)}")
            return False


# Создаем экземпляр кэша для использования в приложении
template_cache = TemplateCache()