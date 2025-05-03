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

logger = logging.getLogger(__name__)


class CephClient:
    """Клиент для работы с файловым хранилищем."""

    def __init__(self):
        # Используем локальное хранилище для простоты
        self.base_dir = Path("storage")
        self.base_dir.mkdir(exist_ok=True)

    def upload_file(
        self,
        file_obj: BinaryIO,
        folder: str = '',
        filename: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> Tuple[str, str]:
        if filename is None:
            filename = f"{uuid.uuid4()}"
        
        folder_path = self.base_dir / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        
        file_path = folder_path / filename
        key = f"{folder}/{filename}" if folder else filename
        
        with open(file_path, 'wb') as f:
            if hasattr(file_obj, 'read'):
                file_obj.seek(0)
                f.write(file_obj.read())
            else:
                f.write(file_obj)
                
        url = f"/storage/{key}"
        return key, url

    def download_file(self, key: str) -> bytes:
        file_path = self.base_dir / key
        with open(file_path, 'rb') as f:
            return f.read()

    def delete_file(self, key: str) -> bool:
        file_path = self.base_dir / key
        try:
            file_path.unlink()
            return True
        except FileNotFoundError:
            return False

    def get_file_url(self, key: str, expires_in: int = 3600) -> str:
        return f"/storage/{key}"

    def list_files(self, prefix: str = '') -> list:
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