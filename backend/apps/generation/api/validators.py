"""
Валидаторы для генерации документов.
"""
from typing import Dict, Any, List, Tuple
from apps.templates.models.template import Template, Field, FieldChoice


class TemplateDataValidator:
    """Валидатор данных для шаблонов."""
    
    @staticmethod
    def validate_template_data(template: Template, data: Dict[str, Any]) -> Tuple[bool, List[Dict[str, str]]]:
        """
        Валидирует данные на соответствие полям шаблона.
        
        Args:
            template: Объект шаблона
            data: Данные для валидации
            
        Returns:
            tuple: (is_valid, errors) - флаг валидности и список ошибок
        """
        errors = []
        
        # Получаем все поля шаблона
        fields = template.fields.all()
        
        # Проверяем обязательные поля
        for field in fields:
            if field.is_required:
                if not field.key in data or data[field.key] is None or str(data[field.key]).strip() == '':
                    errors.append({
                        'field': field.key,
                        'label': field.label,
                        'error': 'Обязательное поле отсутствует или пустое'
                    })
                    continue
            
            # Валидируем только если поле присутствует
            if field.key in data and data[field.key] is not None:
                field_errors = TemplateDataValidator._validate_field(field, data[field.key])
                errors.extend(field_errors)
        
        # Проверяем на лишние поля
        template_field_keys = set(field.key for field in fields)
        data_keys = set(data.keys())
        extra_keys = data_keys - template_field_keys
        
        for extra_key in extra_keys:
            errors.append({
                'field': extra_key,
                'label': extra_key,
                'error': 'Поле не существует в шаблоне'
            })
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_field(field: Field, value: Any) -> List[Dict[str, str]]:
        """
        Валидирует конкретное поле.
        
        Args:
            field: Поле шаблона
            value: Значение для проверки
            
        Returns:
            List[Dict[str, str]]: Список ошибок
        """
        errors = []
        
        if field.type == 'choices':
            # Проверяем, что значение есть среди допустимых
            valid_values = list(field.choices.values_list('value', flat=True))
            
            if str(value) not in map(str, valid_values):
                choices_info = [
                    f"{choice.label} ({choice.value})" 
                    for choice in field.choices.all().order_by('order')
                ]
                errors.append({
                    'field': field.key,
                    'label': field.label,
                    'error': f'Значение должно быть одним из: {", ".join(choices_info)}'
                })
        
        # Дополнительные валидации можно добавить здесь
        # например для email, phone, url и т.д.
        
        return errors
    
    @staticmethod
    def get_template_fields_structure(template: Template) -> Dict[str, Any]:
        """
        Возвращает структуру полей шаблона.
        
        Args:
            template: Шаблон
            
        Returns:
            Dict: Структура полей
        """
        global_fields = []
        page_fields = {}
        
        for field in template.fields.all().order_by('page__index', 'order'):
            field_data = {
                'key': field.key,
                'label': field.label,
                'type': field.type,
                'required': field.is_required,
                'placeholder': field.placeholder,
                'help_text': field.help_text,
            }
            
            if field.default_value:
                field_data['default_value'] = field.default_value
            
            if field.type == 'choices' and field.choices.exists():
                field_data['choices'] = [
                    {
                        'label': choice.label,
                        'value': choice.value,
                        'order': choice.order
                    }
                    for choice in field.choices.all().order_by('order')
                ]
            
            if field.page is None:
                global_fields.append(field_data)
            else:
                page_key = str(field.page.index)
                if page_key not in page_fields:
                    page_fields[page_key] = {
                        'index': field.page.index,
                        'fields': []
                    }
                page_fields[page_key]['fields'].append(field_data)
        
        return {
            'global_fields': global_fields,
            'page_fields': page_fields
        } 