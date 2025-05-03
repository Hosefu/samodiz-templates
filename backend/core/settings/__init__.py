"""
Настройки Django для проекта Самодизайн.
"""
import os

# Определяем, какие настройки использовать
DJANGO_ENV = os.environ.get('DJANGO_ENV', 'local')

if DJANGO_ENV == 'production':
    from .prod import *  # noqa
else:
    from .local import *  # noqa