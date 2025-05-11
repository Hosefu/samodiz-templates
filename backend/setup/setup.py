#!/usr/bin/env python
"""
Скрипт для первоначальной настройки системы Самодизайн.
"""
import os
import sys
import logging
from pathlib import Path
from io import BytesIO

# Настройка путей
SETUP_DIR = Path(__file__).parent
PROJECT_ROOT = SETUP_DIR.parent
sys.path.append(str(PROJECT_ROOT))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    import django
    django.setup()
except Exception as e:
    print(f"Ошибка при инициализации Django: {e}")
    sys.exit(1)

# Импорты после настройки Django
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.templates.models import Unit, Format, FormatSetting, Template, Page, Field, Asset, PageSettings
from apps.templates.models import FieldChoice
from infrastructure.minio_client import minio_client
from apps.templates.services.asset_helper import asset_helper

User = get_user_model()
logger = logging.getLogger(__name__)

# Константы
TEMPLATE_DIR = SETUP_DIR / 'rwb-template'
ASSETS_DIR = TEMPLATE_DIR / 'assets'
HTML_PATH = TEMPLATE_DIR / 'input.html'

# Данные для инициализации
UNITS_DATA = [
    ('mm', 'Миллиметры'),
    ('cm', 'Сантиметры'),
    ('in', 'Дюймы'),
    ('px', 'Пиксели'),
]

FORMATS_DATA = {
    'pdf': {
        'description': 'Portable Document Format (PDF)',
        'render_url': 'http://pdf-renderer:8081/api/render',
        'settings': [
            ('dpi', 'DPI', '300', False),
            ('cmyk_support', 'Поддержка CMYK', 'true', False),
            ('bleeds', 'Припуски под обрез', '0', False),
        ],
        'units': ['mm', 'cm', 'in', 'px']
    },
    'png': {
        'description': 'Portable Network Graphics (PNG)',
        'render_url': 'http://png-renderer:8082/api/render',
        'settings': [
            ('dpi', 'DPI', '300', True),
            ('quality', 'Качество', '100', True),
            ('transparent', 'Прозрачность', 'false', False),
        ],
        'units': ['px']
    },
    'svg': {
        'description': 'Scalable Vector Graphics (SVG)',
        'render_url': 'http://svg-renderer:8083/api/render',
        'settings': [],
        'units': ['px', 'mm', 'cm', 'in']
    }
}

TEMPLATE_DATA = {
    'name': "Визитка RWB",
    'description': "Бизнес-визитка в стиле RWB",
    'fields': [
        {'key': 'last_name', 'label': 'Фамилия', 'order': 1, 'is_required': True},
        {'key': 'first_name', 'label': 'Имя', 'order': 2, 'is_required': True},
        {'key': 'patronymic', 'label': 'Отчество', 'order': 3, 'is_required': True},
        {'key': 'position', 'label': 'Должность', 'order': 4, 'is_required': True},
        {'key': 'address', 'label': 'Адрес', 'order': 5, 'is_required': True},
        {'key': 'phone', 'label': 'Телефон', 'order': 6, 'is_required': True},
        {'key': 'email', 'label': 'Email', 'order': 7, 'is_required': True},
    ],
    'page': {
        'width': 95,
        'height': 65,
        'index': 0
    }
}


class SetupError(Exception):
    """Исключение для ошибок установки."""
    pass


def setup_logging():
    """Настройка логирования."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def ensure_directories():
    """Проверяет наличие необходимых директорий."""
    if not TEMPLATE_DIR.exists():
        raise SetupError(f"Template directory not found: {TEMPLATE_DIR}")
    
    if not HTML_PATH.exists():
        raise SetupError(f"Template HTML file not found: {HTML_PATH}")
    
    if not ASSETS_DIR.exists():
        logger.warning(f"Assets directory not found: {ASSETS_DIR}")


def setup_units():
    """Создает единицы измерения."""
    logger.info("Setting up units...")
    
    for key, name in UNITS_DATA:
        unit, created = Unit.objects.get_or_create(
            key=key,
            defaults={'name': name}
        )
        if created:
            logger.info(f"Created unit: {key} ({name})")
    
    logger.info(f"Units setup complete: {len(UNITS_DATA)} units")


def setup_formats():
    """Создает форматы документов."""
    logger.info("Setting up formats...")
    
    for format_name, format_info in FORMATS_DATA.items():
        # Создаем формат
        format_obj, created = Format.objects.get_or_create(
            name=format_name,
            defaults={
                'description': format_info['description'],
                'render_url': format_info['render_url']
            }
        )
        
        if created:
            logger.info(f"Created format: {format_name}")
        
        # Создаем настройки формата
        for key, name, default, required in format_info['settings']:
            FormatSetting.objects.get_or_create(
                format=format_obj,
                key=key,
                defaults={
                    'name': name,
                    'default_value': default,
                    'is_required': required
                }
            )
        
        # Назначаем поддерживаемые единицы
        for unit_key in format_info['units']:
            try:
                unit = Unit.objects.get(key=unit_key)
                format_obj.allowed_units.add(unit)
            except Unit.DoesNotExist:
                logger.error(f"Unit not found: {unit_key}")
    
    logger.info("Formats setup complete")


def setup_template():
    """Создает базовый шаблон с полями и ассетами."""
    logger.info("Setting up template...")
    
    # Получаем суперпользователя
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        raise SetupError("No admin user found. Create superuser first.")
    
    # Получаем необходимые объекты
    try:
        pdf_format = Format.objects.get(name='pdf')
        mm_unit = Unit.objects.get(key='mm')
    except (Format.DoesNotExist, Unit.DoesNotExist) as e:
        raise SetupError(f"Required objects not found: {e}")
    
    # Проверяем существование шаблона
    if Template.objects.filter(name=TEMPLATE_DATA['name']).exists():
        template = Template.objects.get(name=TEMPLATE_DATA['name'])
        logger.info("Template already exists, updating...")
    else:
        template = None
    
    # Читаем HTML шаблона
    try:
        with open(HTML_PATH, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        raise SetupError(f"Failed to read template HTML: {e}")
    
    with transaction.atomic():
        if template:
            # Обновляем существующий шаблон
            template.html = html_content
            template.save()
            logger.info("Updated template HTML")
        else:
            # Создаем новый шаблон
            template = Template.objects.create(
                name=TEMPLATE_DATA['name'],
                description=TEMPLATE_DATA['description'],
                html=html_content,
                format=pdf_format,
                unit=mm_unit,
                owner=admin,
                is_public=True
            )
            logger.info(f"Created template: {template.name}")
            
            # Создаем страницу
            page_data = TEMPLATE_DATA['page']
            page = Page.objects.create(
                template=template,
                index=page_data['index'],
                html=html_content,
                width=page_data['width'],
                height=page_data['height']
            )
            logger.info(f"Created page {page.index}")
            
            # Создаем настройки страницы
            for setting in pdf_format.expected_settings.all():
                PageSettings.objects.create(
                    page=page,
                    format_setting=setting,
                    value=setting.default_value or '',
                )
            
            # Создаем поля шаблона
            for field_data in TEMPLATE_DATA['fields']:
                Field.objects.create(
                    template=template,
                    page=None,  # Глобальные поля
                    **field_data
                )
            logger.info(f"Created {len(TEMPLATE_DATA['fields'])} fields")
        
        # Загружаем ассеты
        if ASSETS_DIR.exists():
            # Загружаем шрифт
            font_path = ASSETS_DIR / 'InterDisplay-Regular.ttf'
            if font_path.exists():
                try:
                    asset_helper.upload_asset(
                        template_id=str(template.id),
                        file_obj=font_path,
                        filename='InterDisplay-Regular.ttf',
                        mime_type='font/ttf'
                    )
                    logger.info("Font asset uploaded successfully")
                except Exception as e:
                    logger.error(f"Failed to upload font asset: {e}")
            else:
                logger.warning(f"Font file not found: {font_path}")
        
        logger.info("Template setup complete")


def setup_admin():
    """Создает суперпользователя."""
    logger.info("Setting up admin user...")
    
    if User.objects.filter(username='admin').exists():
        logger.info("Admin user already exists")
        return
    
    User.objects.create_superuser(
        username='admin',
        email='admin@samodesign.ru',
        password='admin'
    )
    logger.info("Created admin user")


@transaction.atomic
def main():
    """Основная функция настройки."""
    setup_logging()
    
    try:
        logger.info("Starting initial setup...")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Setup directory: {SETUP_DIR}")
        
        # Проверяем директории
        ensure_directories()
        
        # Создаем базовые данные
        setup_units()
        setup_formats()
        setup_admin()
        setup_template()
        
        logger.info("Setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        logger.exception("Detailed error:")
        sys.exit(1)


if __name__ == '__main__':
    main()