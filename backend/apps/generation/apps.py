"""
Конфигурация приложения генерации документов.
"""
from django.apps import AppConfig


class GenerationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.generation'
    verbose_name = 'Генерация документов'
    
    def ready(self):
        """Инициализация приложения."""
        # Импортируем сигналы здесь, чтобы они были зарегистрированы
        # (если будут нужны в будущем)
        pass 