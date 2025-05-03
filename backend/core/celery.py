"""
Конфигурация Celery для проекта Самодизайн.
"""
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.base')

# Создаем экземпляр приложения Celery
app = Celery('samodes')

# Загружаем конфигурацию из настроек Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим и регистрируем задачи в приложениях Django
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

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