from django.core.management.base import BaseCommand
from infrastructure.minio_client import minio_client

class Command(BaseCommand):
    help = 'Проверяет подключение к MinIO'
    
    def handle(self, *args, **options):
        try:
            # Проверяем подключение
            buckets = [minio_client.templates_bucket, minio_client.documents_bucket]
            
            for bucket in buckets:
                if minio_client.client.bucket_exists(bucket):
                    self.stdout.write(self.style.SUCCESS(f'✓ Bucket {bucket} exists'))
                else:
                    self.stdout.write(self.style.ERROR(f'✗ Bucket {bucket} does not exist'))
            
            # Проверяем создание тестового файла
            from io import BytesIO
            test_content = b"test"
            test_file = BytesIO(test_content)
            
            try:
                key, url = minio_client.upload_file(test_file, 'test', 'test.txt', 'text/plain')
                self.stdout.write(self.style.SUCCESS('✓ File upload works'))
                
                # Удаляем тестовый файл
                minio_client.delete_file(key, 'templates')
                self.stdout.write(self.style.SUCCESS('✓ File deletion works'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error testing file operations: {e}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to connect to MinIO: {e}')) 