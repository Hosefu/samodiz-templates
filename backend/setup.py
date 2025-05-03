#!/usr/bin/env python
"""
Скрипт для первоначальной настройки системы Самодизайн.

Создает базовые форматы, единицы измерения и другие необходимые данные.
"""
import os
import django
import logging
from django.db import transaction

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Импорты моделей (после настройки Django)
from apps.templates.models.unit_format import Unit, Format, FormatSetting

logger = logging.getLogger(__name__)


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


@transaction.atomic
def main():
    """Основная функция настройки."""
    try:
        logger.info("Starting initial setup")
        
        # Создаем базовые единицы измерения
        setup_units()
        
        # Создаем форматы и их настройки
        setup_formats()
        
        logger.info("Setup completed successfully")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        raise


if __name__ == '__main__':
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    main()