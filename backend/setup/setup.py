#!/usr/bin/env python
"""
Скрипт для первоначальной настройки системы Самодизайн.

Создает базовые форматы, единицы измерения и другие необходимые данные.
"""
import os
import sys
import django
import logging
from django.db import transaction
from io import BytesIO
from reversion import revisions

# Добавляем родительскую директорию в sys.path, если скрипт запускается напрямую
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
try:
    django.setup()
except Exception as e:
    print(f"Ошибка при настройке Django: {e}")
    sys.exit(1)

# Импорты моделей (после настройки Django)
from apps.templates.models.unit_format import Unit, Format, FormatSetting
from apps.templates.models.template import Template, Page, Asset, Field
from django.contrib.auth import get_user_model
from infrastructure.ceph import ceph_client

logger = logging.getLogger(__name__)

User = get_user_model()

# Находим абсолютный путь к директории с активами
SETUP_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(SETUP_DIR, 'rwb-template')
ASSETS_DIR = os.path.join(TEMPLATE_DIR, 'assets')
HTML_PATH = os.path.join(TEMPLATE_DIR, 'input.html')

def setup_units():
    """Создает базовые единицы измерения."""
    units = [
        {'key': 'mm', 'name': 'миллиметры'},
        {'key': 'cm', 'name': 'сантиметры'},
        {'key': 'px', 'name': 'пиксели'},
        {'key': 'in', 'name': 'дюймы'},
        {'key': 'pt', 'name': 'пункты'},
    ]
    
    for unit_data in units:
        Unit.objects.get_or_create(
            key=unit_data['key'],
            defaults={'name': unit_data['name']}
        )
    
    logger.info(f"Created {len(units)} units")


def setup_formats():
    """Создает базовые форматы документов и их настройки."""
    # Создаем формат PDF
    pdf_format, _ = Format.objects.get_or_create(
        name='pdf',
        defaults={
            'description': 'Portable Document Format (PDF)',
            'render_url': 'http://pdf-renderer/api/render'
        }
    )
    
    # Настройки для PDF
    pdf_settings = [
        {
            'name': 'CMYK поддержка',
            'description': 'Использовать цветовую модель CMYK вместо RGB',
            'key': 'cmyk_support',
            'is_required': False,
            'default_value': 'false'
        },
        {
            'name': 'Вылеты (мм)',
            'description': 'Размер вылетов в миллиметрах',
            'key': 'bleeds',
            'is_required': False,
            'default_value': '3'
        },
        {
            'name': 'DPI',
            'description': 'Разрешение в точках на дюйм',
            'key': 'dpi',
            'is_required': False,
            'default_value': '300'
        }
    ]
    
    for setting_data in pdf_settings:
        FormatSetting.objects.get_or_create(
            format=pdf_format,
            key=setting_data['key'],
            defaults={
                'name': setting_data['name'],
                'description': setting_data['description'],
                'is_required': setting_data['is_required'],
                'default_value': setting_data['default_value']
            }
        )
    
    # Создаем формат PNG
    png_format, _ = Format.objects.get_or_create(
        name='png',
        defaults={
            'description': 'Portable Network Graphics (PNG)',
            'render_url': 'http://png-renderer/api/render'
        }
    )
    
    # Настройки для PNG
    png_settings = [
        {
            'name': 'DPI',
            'description': 'Разрешение в точках на дюйм',
            'key': 'dpi',
            'is_required': False,
            'default_value': '300'
        },
        {
            'name': 'Прозрачность',
            'description': 'Поддержка прозрачности',
            'key': 'transparency',
            'is_required': False,
            'default_value': 'true'
        }
    ]
    
    for setting_data in png_settings:
        FormatSetting.objects.get_or_create(
            format=png_format,
            key=setting_data['key'],
            defaults={
                'name': setting_data['name'],
                'description': setting_data['description'],
                'is_required': setting_data['is_required'],
                'default_value': setting_data['default_value']
            }
        )
    
    # Создаем формат SVG
    svg_format, _ = Format.objects.get_or_create(
        name='svg',
        defaults={
            'description': 'Scalable Vector Graphics (SVG)',
            'render_url': 'http://svg-renderer/api/render'
        }
    )
    
    # Настройки для SVG
    svg_settings = [
        {
            'name': 'Оптимизация',
            'description': 'Оптимизировать SVG для размера',
            'key': 'optimize',
            'is_required': False,
            'default_value': 'true'
        },
        {
            'name': 'Внедрение шрифтов',
            'description': 'Внедрить шрифты в SVG файл',
            'key': 'embed_fonts',
            'is_required': False,
            'default_value': 'false'
        }
    ]
    
    for setting_data in svg_settings:
        FormatSetting.objects.get_or_create(
            format=svg_format,
            key=setting_data['key'],
            defaults={
                'name': setting_data['name'],
                'description': setting_data['description'],
                'is_required': setting_data['is_required'],
                'default_value': setting_data['default_value']
            }
        )
    
    # Назначаем поддерживаемые единицы измерения для форматов
    mm_unit = Unit.objects.get(key='mm')
    cm_unit = Unit.objects.get(key='cm')
    px_unit = Unit.objects.get(key='px')
    in_unit = Unit.objects.get(key='in')
    pt_unit = Unit.objects.get(key='pt')
    
    # PDF поддерживает все единицы
    pdf_format.allowed_units.add(mm_unit, cm_unit, px_unit, in_unit, pt_unit)
    
    # PNG в основном пиксели
    png_format.allowed_units.add(px_unit)
    
    # SVG поддерживает разные единицы
    svg_format.allowed_units.add(px_unit, mm_unit, cm_unit, in_unit, pt_unit)
    
    logger.info("Created formats and settings")

def setup_template():
    """Создаёт базовый PDF шаблон."""
    # Получаем админа (первого суперпользователя) или создаем его, если его нет
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        logger.warning("No admin user found, skipping template creation")
        return
        
    # Получаем формат PDF и единицу измерения
    try:
        pdf_format = Format.objects.get(name='pdf')
        mm_unit = Unit.objects.get(key='mm')
    except (Format.DoesNotExist, Unit.DoesNotExist):
        logger.error("PDF format or mm unit not found, run setup_formats() first")
        return
    
    # Проверяем, существует ли уже шаблон
    if Template.objects.filter(name="Визитка RWB").exists():
        # Обновляем существующий шаблон для использования нового синтаксиса
        template = Template.objects.get(name="Визитка RWB")
        
        # Читаем обновленный HTML
        try:
            with open(HTML_PATH, 'r', encoding='utf-8') as f:
                html_template = f.read()
            
            template.html = html_template
            template.save()
            
            # Обновляем HTML первой страницы
            first_page = template.pages.first()
            if first_page:
                first_page.html = html_template
                first_page.save()
            
            logger.info("Updated RWB business card template with new asset syntax")
            return
            
        except Exception as e:
            logger.error(f"Error updating template: {e}")
            return
    
    # Создаем новый шаблон
    try:
        with open(HTML_PATH, 'r', encoding='utf-8') as f:
            html_template = f.read()
            
        template = Template.objects.create(
            name="Визитка RWB",
            description="Бизнес-визитка в стиле RWB",
            html=html_template,
            format=pdf_format,
            width=95,
            height=65,
            unit=mm_unit,
            created_by=admin,
            updated_by=admin,
            is_public=True
        )
        
        # Создаем первую страницу
        template.pages.create(
            index=0,
            html=html_template,
            created_by=admin,
            updated_by=admin
        )
        
        logger.info("Created RWB business card template")
        
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        return

@transaction.atomic
def main():
    """Основная функция настройки."""
    try:
        logger.info("Starting initial setup")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Base directory: {BASE_DIR}")
        logger.info(f"Setup directory: {SETUP_DIR}")
        
        # Создаем базовые единицы измерения
        setup_units()
        
        # Создаем форматы и их настройки
        setup_formats()
        
        # Создаем базовый шаблон
        setup_template()
        
        logger.info("Setup completed successfully")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        logger.exception("Detailed error:")
        raise


if __name__ == '__main__':
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    main()