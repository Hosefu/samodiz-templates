"""
Интеграция с Ceph через S3 API для хранения файлов.

Этот модуль обеспечивает взаимодействие с Ceph Object Storage через совместимый с S3 API.
"""
import os
import uuid
import logging
from typing import BinaryIO, Dict, Optional, Tuple, Union
import boto3
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)


class CephClient:
    """Клиент для работы с Ceph S3 API."""

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
        region_name: Optional[str] = None,
    ):
        """
        Инициализирует клиент Ceph S3.
        
        Args:
            endpoint_url: URL для подключения к Ceph (по умолчанию из settings.CEPH_ENDPOINT_URL)
            access_key: Ключ доступа (по умолчанию из settings.CEPH_ACCESS_KEY)
            secret_key: Секретный ключ (по умолчанию из settings.CEPH_SECRET_KEY)
            bucket_name: Имя бакета (по умолчанию из settings.CEPH_BUCKET_NAME)
            region_name: Имя региона (по умолчанию из settings.CEPH_REGION_NAME)
        """
        self.endpoint_url = endpoint_url or settings.CEPH_ENDPOINT_URL
        self.access_key = access_key or settings.CEPH_ACCESS_KEY
        self.secret_key = secret_key or settings.CEPH_SECRET_KEY
        self.bucket_name = bucket_name or settings.CEPH_BUCKET_NAME
        self.region_name = region_name or settings.CEPH_REGION_NAME
        
        # Проверка наличия необходимых настроек
        if not all([self.endpoint_url, self.access_key, self.secret_key, self.bucket_name]):
            raise ValueError("Missing required Ceph S3 configuration parameters")
        
        # Инициализируем S3 клиент
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region_name,
        )
        
        # Создаем бакет, если он не существует
        self.ensure_bucket_exists()
    
    def ensure_bucket_exists(self) -> None:
        """Создает бакет, если он не существует."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            # Если бакет не существует, создаем его
            if e.response['Error']['Code'] == '404':
                logger.info(f"Creating bucket: {self.bucket_name}")
                if self.region_name:
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region_name}
                    )
                else:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                # Другая ошибка
                logger.error(f"Error checking bucket: {e}")
                raise

    def upload_file(
        self,
        file_obj: BinaryIO,
        folder: str = '',
        filename: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Загружает файл в Ceph и возвращает его ключ и URL.
        
        Args:
            file_obj: Объект файла для загрузки
            folder: Папка в бакете (ключ)
            filename: Имя файла (если None, генерируется UUID)
            content_type: MIME-тип файла
        
        Returns:
            Tuple[str, str]: (ключ файла в S3, публичный URL)
        """
        # Генерируем имя файла, если не указано
        if filename is None:
            filename = f"{uuid.uuid4()}"
        
        # Формируем полный ключ с учетом папки
        key = f"{folder}/{filename}" if folder else filename
        
        # Определяем дополнительные параметры
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        
        # Загружаем файл
        try:
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                key,
                ExtraArgs=extra_args
            )
            
            # Формируем публичный URL
            url = f"{self.endpoint_url}/{self.bucket_name}/{key}"
            
            logger.debug(f"Uploaded file to Ceph: {url}")
            return key, url
        
        except ClientError as e:
            logger.error(f"Error uploading file to Ceph: {e}")
            raise

    def download_file(self, key: str) -> bytes:
        """
        Скачивает файл из Ceph по ключу.
        
        Args:
            key: Ключ файла в S3
        
        Returns:
            bytes: Содержимое файла
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"Error downloading file from Ceph: {e}")
            raise

    def delete_file(self, key: str) -> bool:
        """
        Удаляет файл из Ceph по ключу.
        
        Args:
            key: Ключ файла в S3
        
        Returns:
            bool: True, если файл успешно удален
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.debug(f"Deleted file from Ceph: {key}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting file from Ceph: {e}")
            return False

    def get_file_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Генерирует временную URL для доступа к файлу.
        
        Args:
            key: Ключ файла в S3
            expires_in: Время жизни URL в секундах
        
        Returns:
            str: Временный URL для доступа к файлу
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating URL for Ceph file: {e}")
            raise

    def list_files(self, prefix: str = '') -> list:
        """
        Список файлов в бакете с указанным префиксом.
        
        Args:
            prefix: Префикс для фильтрации файлов
        
        Returns:
            list: Список ключей файлов
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                files = [item['Key'] for item in response['Contents']]
            
            return files
        except ClientError as e:
            logger.error(f"Error listing files in Ceph: {e}")
            raise


# Условная инициализация в зависимости от окружения
if os.environ.get('DJANGO_ENV') == 'local':
    # Используем mock для локальной разработки
    from .ceph_mock import MockCephClient as CephClient, ceph_client
else:
    # Создаем реальный инстанс для продакшена
    try:
        ceph_client = CephClient()
    except Exception as e:
        logger.error(f"Failed to initialize Ceph client: {e}")
        # В случае ошибки используем mock
        from .ceph_mock import MockCephClient, ceph_client