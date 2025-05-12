"""
MinIO клиент для работы с файловым хранилищем.
"""
import os
import uuid
import logging
from pathlib import Path
from typing import BinaryIO, Dict, Optional, Tuple, Union
from django.conf import settings
from minio import Minio
from minio.error import S3Error
from datetime import timedelta

logger = logging.getLogger(__name__)


class MinioClientError(Exception):
    """Исключение для ошибок MinIO."""
    pass


class MinioClient:
    """Клиент для работы с MinIO хранилищем."""
    
    def __init__(self):
        """Инициализация клиента MinIO."""
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT_URL.replace('http://', '').replace('https://', ''),
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
            region=settings.MINIO_REGION
        )
        
        # Buckets
        self.templates_bucket = settings.MINIO_BUCKET_TEMPLATES
        self.documents_bucket = settings.MINIO_BUCKET_DOCUMENTS
        
        # Проверяем и создаем buckets если нужно
        self._ensure_buckets_exist()
        
        logger.info(f"MinIO client initialized with endpoint: {settings.MINIO_ENDPOINT_URL}")
    
    def _ensure_buckets_exist(self):
        """Создает buckets если они не существуют."""
        for bucket in [self.templates_bucket, self.documents_bucket]:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket, location=settings.MINIO_REGION)
                    logger.info(f"Created bucket: {bucket}")
            except S3Error as e:
                logger.error(f"Error creating bucket {bucket}: {e}")
    
    def upload_file(
        self,
        file_obj: BinaryIO,
        folder: str = '',
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
        bucket_type: str = 'templates'
    ) -> Tuple[str, str]:
        """
        Загружает файл в MinIO.
        
        Args:
            file_obj: Файловый объект
            folder: Папка для сохранения
            filename: Имя файла (если None, будет сгенерировано)
            content_type: MIME тип
            bucket_type: 'templates' или 'documents'
            
        Returns:
            Tuple[str, str]: (object_name, public_url)
        """
        if filename is None:
            filename = f"{uuid.uuid4()}"
        
        # Определяем bucket
        bucket = self.templates_bucket if bucket_type == 'templates' else self.documents_bucket
        
        # Создаем object_name
        object_name = f"{folder}/{filename}" if folder else filename
        
        try:
            # Создаем базовые metadata
            metadata = {}
            if content_type:
                metadata['Content-Type'] = content_type
            
            # Перематываем файл в начало если это возможно
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
            
            # Определяем размер файла
            if hasattr(file_obj, 'getvalue'):
                length = len(file_obj.getvalue())
            elif hasattr(file_obj, 'size'):
                length = file_obj.size
            else:
                # Для LocalFile и других объектов
                current_pos = file_obj.tell()
                file_obj.seek(0, 2)  # Seek to end
                length = file_obj.tell()
                file_obj.seek(current_pos)  # Return to original position
            
            # Загружаем файл в MinIO
            try:
                self.client.put_object(
                    Bucket=bucket,
                    Key=object_name,
                    Data=file_obj,
                    Length=length,
                    ContentType=content_type
                )
                logger.info(f"Файл {filename} успешно загружен в {bucket}/{object_name}")
            except S3Error as e:
                logger.error(f"Ошибка загрузки файла в MinIO: {e}")
                raise
            
            # Формируем URL объекта
            if bucket_type == 'documents':
                object_url = f"generated-documents/{object_name}"
            else:
                object_url = f"{bucket_type}-assets/{object_name}"
            
            return object_name, object_url
            
        except S3Error as e:
            logger.error(f"Error uploading to MinIO: {e}")
            raise MinioClientError(f"Failed to upload file: {str(e)}")
    
    def download_file(self, object_name: str, bucket_type: str = 'templates') -> bytes:
        """
        Загружает файл из MinIO.
        
        Args:
            object_name: Имя объекта
            bucket_type: 'templates' или 'documents'
            
        Returns:
            bytes: Содержимое файла
        """
        bucket = self.templates_bucket if bucket_type == 'templates' else self.documents_bucket
        
        try:
            response = self.client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
            
        except S3Error as e:
            logger.error(f"Error downloading from MinIO: {e}")
            raise MinioClientError(f"Failed to download file: {str(e)}")
    
    def delete_file(self, object_name: str, bucket_type: str = 'templates') -> bool:
        """
        Удаляет файл из MinIO.
        
        Args:
            object_name: Имя объекта
            bucket_type: 'templates' или 'documents'
            
        Returns:
            bool: True если успешно удален
        """
        bucket = self.templates_bucket if bucket_type == 'templates' else self.documents_bucket
        
        try:
            self.client.remove_object(bucket, object_name)
            return True
            
        except S3Error as e:
            logger.error(f"Error deleting from MinIO: {e}")
            return False
    
    def get_presigned_url(
        self, 
        object_name: str, 
        bucket_type: str = 'templates',
        expires: timedelta = timedelta(hours=1)
    ) -> str:
        """
        Генерирует подписанный URL для доступа к файлу.
        
        Args:
            object_name: Имя объекта
            bucket_type: 'templates' или 'documents'
            expires: Время истечения ссылки
            
        Returns:
            str: Подписанный URL
        """
        bucket = self.templates_bucket if bucket_type == 'templates' else self.documents_bucket
        
        try:
            url = self.client.presigned_get_object(
                bucket_name=bucket,
                object_name=object_name,
                expires=expires
            )
            return url
            
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise MinioClientError(f"Failed to generate presigned URL: {str(e)}")
    
    def list_objects(self, prefix: str = '', bucket_type: str = 'templates') -> list:
        """
        Получает список объектов в bucket.
        
        Args:
            prefix: Префикс для фильтрации
            bucket_type: 'templates' или 'documents'
            
        Returns:
            list: Список имен объектов
        """
        bucket = self.templates_bucket if bucket_type == 'templates' else self.documents_bucket
        
        try:
            objects = []
            for obj in self.client.list_objects(bucket, prefix=prefix, recursive=True):
                objects.append(obj.object_name)
            return objects
            
        except S3Error as e:
            logger.error(f"Error listing objects: {e}")
            return []


# Создаем singleton
minio_client = MinioClient() 