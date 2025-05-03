"""
Динамический выбор настроек Django с помощью DJANGO_SETTINGS_MODULE.
По умолчанию используются локальные настройки для разработки.
"""
import os

# Определяем настройки на основе переменной окружения DJANGO_SETTINGS_MODULE
# Если не указано - используем local.py
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'core.settings.local')

# На основе значения переменной импортируем соответствующий модуль
if settings_module == 'core.settings.prod':
    from .prod import *  # noqa
elif settings_module == 'core.settings.local':
    from .local import *  # noqa
else:
    # По умолчанию используем локальные настройки
    from .local import *  # noqa