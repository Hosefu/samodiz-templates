from django.core.management.base import BaseCommand
import requests
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Проверяет доступность сервисов рендеринга'
    
    def handle(self, *args, **options):
        # Импортируем модель Format тут для предотвращения циклических импортов
        from apps.templates.models import Format
        
        # Получаем все форматы из БД
        formats = Format.objects.all()
        
        if not formats.exists():
            self.stdout.write(self.style.WARNING('Форматы не найдены в базе данных. Сначала запустите setup.py'))
            return
            
        for fmt in formats:
            # Преобразуем URL рендеринга в URL health-check
            health_url = fmt.render_url.replace('/api/render', '/health')
            
            try:
                self.stdout.write(f"Проверка рендерера {fmt.name} ({health_url})...")
                response = requests.get(health_url, timeout=5)
                status = "OK" if response.ok else "ОШИБКА"
                self.stdout.write(f"{fmt.name}: {status}")
                if not response.ok:
                    self.stdout.write(f"  Ответ: {response.text}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"{fmt.name}: НЕДОСТУПЕН ({e})")) 