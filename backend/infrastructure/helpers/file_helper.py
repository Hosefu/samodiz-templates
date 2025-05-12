"""
Хелпер для работы с файлами.
"""
import logging
from typing import BinaryIO, Optional, Union, Tuple
from pathlib import Path
from io import BytesIO
from datetime import timedelta
from urllib.parse import urlparse
from django.conf import settings

from infrastructure.helpers.base_helper import BaseHelper
from infrastructure.minio_client import minio_client

logger = logging.getLogger(__name__)


class FileHelper(BaseHelper):
    """
    Базовый класс для хелперов, работающих с файлами.
    
    Предоставляет общие методы для работы с файлами и хранилищем.
    """
    
    @classmethod
    def get_presigned_url(
        cls,
        file_path: str, 
        bucket_type: str, 
        expires: timedelta = timedelta(hours=24)
    ) -> str:
        """
        Генерирует подписанный URL для объекта в хранилище.
        
        Args:
            file_path: Путь к файлу или полный URL
            bucket_type: Тип бакета ('templates' или 'documents')
            expires: Время действия подписанной ссылки
            
        Returns:
            str: Подписанный URL или исходный путь в случае ошибки
        """
        if not file_path:
            return ""
        
        try:
            # Парсим путь для извлечения object_name
            parsed_url = urlparse(file_path)
            path_parts = parsed_url.path.strip('/').split('/')
            
            # Определяем имя бакета для проверки
            bucket_name = f"{bucket_type}-assets" if bucket_type == 'templates' else bucket_type
            
            # Извлекаем имя объекта из пути
            if len(path_parts) >= 1:
                # Проверяем наличие паттерна дублирования пути
                if len(path_parts) >= 2 and path_parts[0] == bucket_name and path_parts[1] == bucket_name:
                    # Если обнаружено дублирование (bucket_name/bucket_name/...)
                    object_name = '/'.join(path_parts[1:])
                    cls.log_error(f"Обнаружено дублирование пути в URL: {file_path}", level='warning')
                # Если первая часть - имя бакета, удаляем её
                elif path_parts[0] == bucket_name and len(path_parts) > 1:
                    object_name = '/'.join(path_parts[1:])
                else:
                    object_name = '/'.join(path_parts)
                
                # Генерируем подписанную ссылку
                presigned_url = minio_client.get_presigned_url(
                    object_name=object_name,
                    bucket_type=bucket_type,
                    expires=expires
                )
                
                # Преобразуем внутренний URL в публичный
                public_base_url = settings.MINIO_PUBLIC_BASE_URL
                presigned_url = presigned_url.replace('http://minio:9000', public_base_url)
                
                return presigned_url
            else:
                cls.log_error(f"Invalid file path format", level='warning')
                return file_path
                
        except Exception as e:
            cls.log_error(f"Error generating presigned URL for {file_path}", e)
            return file_path
    
    @classmethod
    def upload_file(
        cls,
        file_obj: Union[BinaryIO, Path, str, bytes],
        folder: str,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
        bucket_type: str = 'templates'
    ) -> Tuple[str, str]:
        """
        Загружает файл в хранилище.
        
        Args:
            file_obj: Файловый объект, путь к файлу или байты
            folder: Папка для сохранения
            filename: Имя файла (если None, будет сгенерировано)
            mime_type: MIME тип
            bucket_type: 'templates' или 'documents'
            
        Returns:
            tuple: (object_name, url)
        """
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
            mime_type = cls._get_mime_type(ext)
        
        try:
            # Загружаем файл в MinIO
            return minio_client.upload_file(
                file_obj=file_obj,
                folder=folder,
                filename=filename,
                content_type=mime_type,
                bucket_type=bucket_type
            )
        except Exception as e:
            cls.log_error(f"Failed to upload file {filename}", e)
            raise
    
    @classmethod
    def delete_file(cls, object_name: str, bucket_type: str = 'templates') -> bool:
        """
        Удаляет файл из хранилища.
        
        Args:
            object_name: Имя объекта
            bucket_type: 'templates' или 'documents'
            
        Returns:
            bool: True если успешно удален
        """
        try:
            # Удаляем файл из MinIO
            return minio_client.delete_file(object_name, bucket_type)
        except Exception as e:
            cls.log_error(f"Failed to delete file {object_name}", e)
            return False
    
    @staticmethod
    def _get_mime_type(ext: str) -> str:
        """Определяет MIME-тип по расширению файла."""
        # Словарь соответствия расширений файлов MIME-типам
        mime_types = {
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
        
        return mime_types.get(ext, 'application/octet-stream') 