"""
Mock Ceph клиент для локальной разработки.
"""
import os


class MockCephClient:
    """Mock клиент для имитации работы с Ceph."""

    def __init__(self):
        """Инициализация Mock клиента."""
        self.base_dir = "mock_storage"
        os.makedirs(self.base_dir, exist_ok=True)

    def upload_file(self, file_obj, folder='', filename=None, content_type=None):
        """Mock загрузки файла."""
        if filename is None:
            filename = f"file_{os.getpid()}.bin"
        
        folder_path = os.path.join(self.base_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        
        file_path = os.path.join(folder_path, filename)
        key = f"{folder}/{filename}"
        
        # Сохраняем файл локально
        with open(file_path, 'wb') as f:
            if hasattr(file_obj, 'read'):
                file_obj.seek(0)
                f.write(file_obj.read())
            else:
                f.write(file_obj)
                
        url = f"file://{os.path.abspath(file_path)}"
        return key, url

    def download_file(self, key):
        """Mock загрузки файла."""
        file_path = os.path.join(self.base_dir, key)
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            return None

    def delete_file(self, key):
        """Mock удаления файла."""
        file_path = os.path.join(self.base_dir, key)
        try:
            os.remove(file_path)
            return True
        except FileNotFoundError:
            return False

    def get_file_url(self, key, expires_in=3600):
        """Mock генерации URL."""
        file_path = os.path.join(self.base_dir, key)
        return f"file://{os.path.abspath(file_path)}"

    def list_files(self, prefix=''):
        """Mock получения списка файлов."""
        files = []
        search_path = os.path.join(self.base_dir, prefix)
        
        if os.path.exists(search_path):
            for root, _, filenames in os.walk(search_path):
                for filename in filenames:
                    rel_path = os.path.relpath(os.path.join(root, filename), self.base_dir)
                    files.append(rel_path)
        
        return files


# Создаем mock инстанс для локальной разработки
ceph_client = MockCephClient() 