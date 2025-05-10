"""
Сервис валидации полей шаблона.
"""
from typing import Any, Dict, Optional
import re
from datetime import datetime
from urllib.parse import urlparse
from apps.templates.models.template import Field


class FieldValidator:
    """Валидация полей на основе их типов."""
    
    @staticmethod
    def validate_field(field: Field, value: Any) -> tuple[bool, Optional[str]]:
        """
        Валидирует значение поля.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if field.type == 'choices':
            return FieldValidator._validate_choice(field, value)
        else:  # string
            return FieldValidator._validate_string(field, value)
    
    @staticmethod
    def _validate_choice(field: Field, value: str) -> tuple[bool, Optional[str]]:
        """Валидация выбора из списка."""
        if not value:
            return True, None
        
        valid_values = list(field.choices.values_list('value', flat=True))
        
        if value not in valid_values:
            valid_labels = [f"{choice.label} ({choice.value})" for choice in field.choices.all()]
            return False, f"Значение должно быть одним из: {', '.join(valid_labels)}"
        
        return True, None
    
    @staticmethod
    def _validate_string(field: Field, value: str) -> tuple[bool, Optional[str]]:
        """Валидация строкового поля."""
        if not value:
            return True, None
        
        # Базовая валидация - можно расширить при необходимости
        if field.placeholder:
            # Здесь можно добавить дополнительную валидацию по шаблону placeholder
            pass
        
        return True, None
    
    @staticmethod
    def _validate_email(value: str) -> tuple[bool, Optional[str]]:
        """Валидация email."""
        if not value:
            return True, None
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            return False, "Неверный формат email"
        
        return True, None
    
    @staticmethod
    def _validate_phone(value: str, pattern: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """Валидация телефона."""
        if not value:
            return True, None
        
        # Очищаем телефон от лишних символов
        clean_phone = re.sub(r'[^\d+]', '', value)
        
        if pattern:
            if not re.match(pattern, value):
                return False, "Неверный формат телефона"
        elif not re.match(r'^\+?[1-9]\d{1,14}$', clean_phone):
            return False, "Неверный формат телефона"
        
        return True, None
    
    @staticmethod
    def _validate_number(value: Any, attributes: Dict) -> tuple[bool, Optional[str]]:
        """Валидация числа."""
        if value is None or value == '':
            return True, None
        
        try:
            num = float(value)
            
            if 'min' in attributes and num < attributes['min']:
                return False, f"Значение должно быть не меньше {attributes['min']}"
            
            if 'max' in attributes and num > attributes['max']:
                return False, f"Значение должно быть не больше {attributes['max']}"
            
            return True, None
        except (ValueError, TypeError):
            return False, "Должно быть числом"
    
    @staticmethod
    def _validate_date(value: str, date_format: str) -> tuple[bool, Optional[str]]:
        """Валидация даты."""
        if not value:
            return True, None
        
        try:
            datetime.strptime(value, date_format)
            return True, None
        except ValueError:
            return False, f"Дата должна быть в формате {date_format}"
    
    @staticmethod
    def _validate_multi_choice(value: list, choices: list) -> tuple[bool, Optional[str]]:
        """Валидация множественного выбора."""
        if not value:
            return True, None
        
        if not isinstance(value, list):
            return False, "Должен быть списком значений"
        
        valid_values = [choice.get('value') if isinstance(choice, dict) else choice for choice in choices]
        
        for item in value:
            if item not in valid_values:
                return False, f"Значение '{item}' не допустимо. Допустимые: {', '.join(map(str, valid_values))}"
        
        return True, None
    
    @staticmethod
    def _validate_url(value: str) -> tuple[bool, Optional[str]]:
        """Валидация URL."""
        if not value:
            return True, None
        
        try:
            result = urlparse(value)
            if not all([result.scheme, result.netloc]):
                return False, "Неверный формат URL"
            
            if result.scheme not in ['http', 'https']:
                return False, "URL должен начинаться с http:// или https://"
            
            return True, None
        except Exception:
            return False, "Неверный формат URL"
    
    @staticmethod
    def _validate_text(value: str, attributes: Dict) -> tuple[bool, Optional[str]]:
        """Валидация текста."""
        if not value:
            return True, None
        
        if 'minlength' in attributes and len(value) < attributes['minlength']:
            return False, f"Минимальная длина {attributes['minlength']} символов"
        
        if 'maxlength' in attributes and len(value) > attributes['maxlength']:
            return False, f"Максимальная длина {attributes['maxlength']} символов"
        
        if 'pattern' in attributes and not re.match(attributes['pattern'], value):
            return False, "Значение не соответствует требуемому формату"
        
        return True, None 