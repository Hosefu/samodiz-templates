from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
import os
from typing import Optional


class Settings(BaseSettings):
    """
    Настройки приложения png-renderer
    """
    # Базовые настройки
    APP_NAME: str = "png-renderer"
    DEBUG: bool = Field(default=False)
    
    # Настройки сервера
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8082)
    
    # Настройки кэша
    CACHE_DIR: str = Field(default="/tmp/png-renderer/cache")
    CACHE_ENABLED: bool = Field(default=True)
    CACHE_EXPIRATION: int = Field(default=3600)  # в секундах
    
    # Настройки рендеринга
    DEFAULT_DPI: int = Field(default=96)
    DEFAULT_FORMAT: str = Field(default="png")
    DEFAULT_QUALITY: int = Field(default=90)
    TIMEOUT: int = Field(default=30)  # в секундах
    
    # Пути к временным файлам
    TEMP_DIR: str = Field(default="./temp")
    OUTPUT_DIR: str = Field(default="./output")
    
    # Настройки логгирования
    LOG_LEVEL: str = Field(default="INFO")
    
    # Настройки Playwright
    BROWSER_TYPE: str = Field(default="chromium")  # chromium, firefox, webkit
    BROWSER_HEADLESS: bool = Field(default=True)
    BROWSER_ARGS: list = Field(default=["--no-sandbox", "--disable-setuid-sandbox"])
    
    # Максимальное количество параллельных браузеров
    MAX_CONCURRENT_BROWSERS: int = Field(default=5)
    
    # Максимальный размер HTML в байтах
    MAX_HTML_SIZE: int = Field(default=10_000_000)  # 10MB
    
    # Таймаут для операций рендеринга в секундах
    RENDER_TIMEOUT: int = Field(default=60)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "PNG_RENDERER_"
        case_sensitive = True


def get_settings():
    """
    Получение настроек приложения
    """
    settings = Settings()
    
    # Создаем необходимые директории
    os.makedirs(settings.CACHE_DIR, exist_ok=True)
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    return settings


settings = get_settings()