"""
Обратная совместимость с MinIO.
"""
from .minio_client import minio_client as _minio_client


class CephClient:
    """Класс для обратной совместимости с существующим кодом."""
    
    def __init__(self):
        self._client = _minio_client
    
    def upload_file(self, file_obj, folder='', filename=None, content_type=None):
        """Загружает файл."""
        # Определяем тип bucket по папке
        bucket_type = 'documents' if folder.startswith('documents/') else 'templates'
        return self._client.upload_file(file_obj, folder, filename, content_type, bucket_type)
    
    def download_file(self, key):
        """Загружает файл."""
        # Определяем тип bucket по ключу
        bucket_type = 'documents' if key.startswith('documents/') else 'templates'
        return self._client.download_file(key, bucket_type)
    
    def delete_file(self, key):
        """Удаляет файл."""
        # Определяем тип bucket по ключу
        bucket_type = 'documents' if key.startswith('documents/') else 'templates'
        return self._client.delete_file(key, bucket_type)
    
    def get_file_url(self, key, expires_in=3600):
        """Генерирует URL для файла."""
        from datetime import timedelta
        
        # Определяем тип bucket по ключу
        bucket_type = 'documents' if key.startswith('documents/') else 'templates'
        expires = timedelta(seconds=expires_in)
        
        if bucket_type == 'templates':
            # Для публичных шаблонов используем прямые ссылки
            from django.conf import settings
            return f"{settings.MINIO_PUBLIC_URL}/{key}"
        else:
            # Для документов всегда используем подписанные ссылки
            return self._client.get_presigned_url(key, bucket_type, expires)
    
    def list_files(self, prefix=''):
        """Получает список файлов."""
        # Определяем тип bucket по префиксу
        bucket_type = 'documents' if prefix.startswith('documents/') else 'templates'
        return self._client.list_objects(prefix, bucket_type)


# Создаем singleton для совместимости
ceph_client = CephClient()