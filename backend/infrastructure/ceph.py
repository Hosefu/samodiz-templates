"""
Интеграция с Ceph через S3 API для хранения файлов.

Этот модуль обеспечивает взаимодействие с Ceph Object Storage через совместимый с S3 API.
"""
import os
import uuid
import logging
import shutil
from pathlib import Path
from typing import BinaryIO, Dict, Optional, Tuple, Union
from django.conf import settings

logger = logging.getLogger(__name__)


class CephClient:
    """Клиент для работы с файловым хранилищем."""

    def __init__(self):
        # Проверяем, нужно ли использовать S3 API или локальное хранилище
        self.use_s3 = getattr(settings, 'USE_S3_STORAGE', False)
        
        if self.use_s3:
            # Инициализация S3 клиента
            try:
                import boto3
                from botocore.exceptions import ClientError
                
                self.s3 = boto3.client(
                    's3',
                    endpoint_url=settings.CEPH_ENDPOINT_URL,
                    aws_access_key_id=settings.CEPH_ACCESS_KEY,
                    aws_secret_access_key=settings.CEPH_SECRET_KEY,
                    region_name=getattr(settings, 'CEPH_REGION', 'default'),
                )
                self.bucket = settings.CEPH_BUCKET_NAME
                self.public_url = settings.CEPH_PUBLIC_URL
                logger.info(f"Using S3 storage with endpoint {settings.CEPH_ENDPOINT_URL}")
            except (ImportError, AttributeError) as e:
                logger.error(f"Failed to initialize S3 client: {e}")
                # Если не удалось создать S3 клиент, используем локальное хранилище
                self.use_s3 = False
        
        if not self.use_s3:
            # Инициализация локального хранилища
            self.base_dir = Path("storage")
            self.base_dir.mkdir(exist_ok=True)
            logger.info(f"Using local storage in {self.base_dir}")

    def upload_file(
        self,
        file_obj: BinaryIO,
        folder: str = '',
        filename: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> Tuple[str, str]:
        if filename is None:
            filename = f"{uuid.uuid4()}"
        
        # Создаем ключ объекта
        key = f"{folder}/{filename}" if folder else filename
        
        if self.use_s3:
            try:
                # Дополнительные параметры
                extra_args = {}
                if content_type:
                    extra_args['ContentType'] = content_type
                
                # Если объект - BytesIO или аналогичный, перематываем его
                if hasattr(file_obj, 'seek'):
                    file_obj.seek(0)
                
                # Загружаем файл в S3
                self.s3.upload_fileobj(file_obj, self.bucket, key, ExtraArgs=extra_args)
                
                # Генерируем URL
                url = f"{self.public_url}/{key}"
                return key, url
                
            except Exception as e:
                logger.error(f"Error uploading to S3: {e}")
                raise
        else:
            # Локальное хранилище
            folder_path = self.base_dir / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            
            file_path = folder_path / filename
            
            with open(file_path, 'wb') as f:
                if hasattr(file_obj, 'read'):
                    file_obj.seek(0)
                    f.write(file_obj.read())
                else:
                    f.write(file_obj)
                    
            url = f"/storage/{key}"
            return key, url

    def download_file(self, key: str) -> bytes:
        if self.use_s3:
            try:
                from io import BytesIO
                
                # Создаем буфер
                buffer = BytesIO()
                
                # Загружаем файл из S3 в буфер
                self.s3.download_fileobj(self.bucket, key, buffer)
                
                # Перематываем буфер и возвращаем содержимое
                buffer.seek(0)
                return buffer.read()
                
            except Exception as e:
                logger.error(f"Error downloading from S3: {e}")
                raise
        else:
            # Локальное хранилище
            file_path = self.base_dir / key
            with open(file_path, 'rb') as f:
                return f.read()

    def delete_file(self, key: str) -> bool:
        if self.use_s3:
            try:
                # Удаляем объект из S3
                self.s3.delete_object(Bucket=self.bucket, Key=key)
                return True
                
            except Exception as e:
                logger.error(f"Error deleting from S3: {e}")
                return False
        else:
            # Локальное хранилище
            file_path = self.base_dir / key
            try:
                file_path.unlink()
                return True
            except FileNotFoundError:
                return False

    def get_file_url(self, key: str, expires_in: int = 3600) -> str:
        if self.use_s3:
            try:
                # Для приватных бакетов - генерируем временную подписанную ссылку
                if getattr(settings, 'CEPH_USE_PRESIGNED_URLS', False):
                    url = self.s3.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': self.bucket, 'Key': key},
                        ExpiresIn=expires_in
                    )
                    return url
                else:
                    # Для публичных бакетов - просто возвращаем URL
                    return f"{self.public_url}/{key}"
                    
            except Exception as e:
                logger.error(f"Error generating URL: {e}")
                return f"/storage/{key}"  # Fallback
        else:
            # Локальное хранилище
            return f"/storage/{key}"

    def list_files(self, prefix: str = '') -> list:
        if self.use_s3:
            try:
                # Получаем список объектов из S3
                response = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
                
                # Формируем список ключей
                files = []
                if 'Contents' in response:
                    for obj in response['Contents']:
                        files.append(obj['Key'])
                return files
                
            except Exception as e:
                logger.error(f"Error listing S3 objects: {e}")
                return []
        else:
            # Локальное хранилище
            files = []
            search_path = self.base_dir / prefix
            
            if search_path.exists():
                for file in search_path.rglob('*'):
                    if file.is_file():
                        rel_path = file.relative_to(self.base_dir)
                        files.append(str(rel_path))
            
            return files

# Создаем единственный инстанс
ceph_client = CephClient()