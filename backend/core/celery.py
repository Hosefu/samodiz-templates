"""
Конфигурация Celery для проекта Самодизайн.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Устанавливаем переменную окружения по умолчанию
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Создаем экземпляр Celery
app = Celery('samodesign')

# Загружаем настройки из Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем задачи в приложениях Django
app.autodiscover_tasks()

# Определяем периодические задачи
app.conf.beat_schedule = {
    'cleanup-deleted-files': {
        'task': 'apps.generation.tasks.cleanup.cleanup_deleted',
        'schedule': crontab(hour=3, minute=0),  # Каждый день в 3:00
        'args': (),
    },
}

@app.task(bind=True)
def debug_task(self):
    """Диагностическая задача для проверки работоспособности Celery."""
    print(f'Request: {self.request!r}')