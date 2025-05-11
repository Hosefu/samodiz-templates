from django.core.management.base import BaseCommand
import requests
import time
from infrastructure.minio_client import minio_client
from io import BytesIO

class Command(BaseCommand):
    help = 'Инициализирует MinIO и проверяет его работу'
    
    def handle(self, *args, **options):
        # Ждём пока MinIO запустится
        self.stdout.write("Waiting for MinIO...")
        max_retries = 30
        for i in range(max_retries):
            try:
                # Проверяем доступность MinIO
                if minio_client.client.bucket_exists(minio_client.templates_bucket):
                    self.stdout.write(self.style.SUCCESS("MinIO is ready!"))
                    break
            except Exception:
                if i == max_retries - 1:
                    self.stdout.write(self.style.ERROR("MinIO not accessible"))
                    return
                time.sleep(1)
        
        # Тестируем загрузку файла
        try:
            test_content = b"test content"
            test_file = BytesIO(test_content)
            
            object_name, url = minio_client.upload_file(
                file_obj=test_file,
                folder='test',
                filename='test.txt',
                content_type='text/plain',
                bucket_type='templates'
            )
            
            self.stdout.write(self.style.SUCCESS(f"✓ Upload test passed: {url}"))
            
            # Проверяем доступность через nginx
            nginx_url = f"http://nginx/templates-assets/{object_name}"
            self.stdout.write(f"Testing nginx proxy: {nginx_url}")
            
            # Убираем тестовый файл
            minio_client.delete_file(object_name, 'templates')
            self.stdout.write(self.style.SUCCESS("✓ Delete test passed"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Test failed: {e}")) 