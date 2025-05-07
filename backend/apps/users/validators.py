import re
from typing import List, Dict, Any, Optional
from django.core.exceptions import ValidationError
import unicodedata


def contains_emoji(text: str) -> bool:
    """Проверяет, содержит ли текст эмодзи."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # эмодзи лица
        "\U0001F300-\U0001F5FF"  # символы и пиктограммы
        "\U0001F680-\U0001F6FF"  # транспорт и символы карт
        "\U0001F700-\U0001F77F"  # алхимические символы
        "\U0001F780-\U0001F7FF"  # геометрические фигуры
        "\U0001F800-\U0001F8FF"  # дополнительные стрелки
        "\U0001F900-\U0001F9FF"  # дополнительные символы
        "\U0001FA00-\U0001FA6F"  # шахматные символы
        "\U0001FA70-\U0001FAFF"  # символы лица-рука
        "\U00002702-\U000027B0"  # другие символы
        "\U000024C2-\U0001F251" 
        "]+"
    )
    return bool(emoji_pattern.search(text))


def has_unprintable_characters(text: str) -> bool:
    """Проверяет наличие непечатаемых символов в тексте."""
    for char in text:
        cat = unicodedata.category(char)
        # Категории Control, Format, Unassigned, Private Use и Surrogate
        if cat.startswith(('C', 'Z')):
            return True
    return False


def contains_spam_words(text: str) -> bool:
    """Проверяет наличие спам-слов в тексте."""
    spam_words = [
        'viagra', 'casino', 'lottery', 'prize', 'winner', 
        'free', 'money', 'bitcoin', 'crypto', 'investment',
        'wealthy', 'rich', 'income', 'scam', 'spam'
    ]
    
    text_lower = text.lower()
    for word in spam_words:
        if word in text_lower:
            return True
    return False


class StrongPasswordValidator:
    """Валидатор сложного пароля с настраиваемыми параметрами."""
    
    def __init__(
        self, 
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_numbers: bool = True,
        require_special: bool = True,
        reject_common: bool = True
    ):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_numbers = require_numbers
        self.require_special = require_special
        self.reject_common = reject_common
        
        # Список распространенных паролей
        self.common_passwords = [
            'password', '123456', 'qwerty', 'admin', 'welcome',
            'password123', 'abc123', '12345678', 'qwerty123', 'letmein'
        ]
    
    def validate(self, password: str, user=None) -> None:
        """Валидирует пароль по заданным критериям."""
        errors = []
        
        # Проверка минимальной длины
        if len(password) < self.min_length:
            errors.append(f"Пароль должен содержать не менее {self.min_length} символов.")
        
        # Проверка на заглавные буквы
        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Пароль должен содержать хотя бы одну заглавную букву.")
        
        # Проверка на строчные буквы
        if self.require_lowercase and not any(c.islower() for c in password):
            errors.append("Пароль должен содержать хотя бы одну строчную букву.")
        
        # Проверка на цифры
        if self.require_numbers and not any(c.isdigit() for c in password):
            errors.append("Пароль должен содержать хотя бы одну цифру.")
        
        # Проверка на специальные символы
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Пароль должен содержать хотя бы один специальный символ.")
        
        # Проверка на распространенные пароли
        if self.reject_common and password.lower() in self.common_passwords:
            errors.append("Пароль слишком распространенный и легко угадывается.")
        
        # Проверка на эмодзи и непечатаемые символы
        if contains_emoji(password):
            errors.append("Пароль не должен содержать эмодзи.")
        
        if has_unprintable_characters(password):
            errors.append("Пароль содержит недопустимые непечатаемые символы.")
        
        # Если есть ошибки, выбрасываем исключение
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self) -> str:
        """Возвращает текст справки для этого валидатора."""
        help_texts = [
            f"Пароль должен содержать не менее {self.min_length} символов."
        ]
        
        if self.require_uppercase:
            help_texts.append("Должен содержать хотя бы одну заглавную букву.")
        
        if self.require_lowercase:
            help_texts.append("Должен содержать хотя бы одну строчную букву.")
        
        if self.require_numbers:
            help_texts.append("Должен содержать хотя бы одну цифру.")
        
        if self.require_special:
            help_texts.append("Должен содержать хотя бы один специальный символ.")
        
        return " ".join(help_texts)


class EmailUsernamePasswordValidator:
    """Проверяет, что пароль не совпадает и не похож на email."""
    
    def validate(self, password: str, user=None) -> None:
        if not user:
            return
        
        # Получаем email
        email = getattr(user, 'email', '')
        email_name = email.split('@')[0] if '@' in email else ''
        
        # Если пароль содержит часть email
        if email_name and len(email_name) > 3 and email_name.lower() in password.lower():
            raise ValidationError(
                "Пароль не должен содержать часть вашего email-адреса."
            )
    
    def get_help_text(self) -> str:
        return "Пароль не должен содержать часть вашего email-адреса."


class EmailValidator:
    """Расширенная валидация email с дополнительными проверками."""
    
    def __init__(self):
        # Базовый паттерн для проверки email
        self.email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        
        # Список доменов временных почтовых ящиков
        self.disposable_domains = [
            'tempmail.com', 'temp-mail.org', 'guerrillamail.com', 'mailinator.com',
            'yopmail.com', 'maildrop.cc', '10minutemail.com', 'throwawaymail.com'
        ]
    
    def validate(self, email: str) -> List[str]:
        """Валидирует email и возвращает список ошибок."""
        errors = []
        
        # Проверка формата email
        if not self.email_pattern.match(email):
            errors.append("Некорректный формат email.")
        
        # Разбиваем email на части
        try:
            local_part, domain = email.rsplit('@', 1)
        except ValueError:
            return errors
        
        # Проверяем длину локальной части
        if len(local_part) < 2:
            errors.append("Локальная часть email слишком короткая.")
        
        # Проверка на временные почтовые ящики
        if any(d in domain.lower() for d in self.disposable_domains):
            errors.append("Нельзя использовать временные почтовые адреса.")
        
        # Проверка на emoji и непечатаемые символы
        if contains_emoji(email) or has_unprintable_characters(email):
            errors.append("Email содержит недопустимые символы.")
        
        # Проверка на спам-слова
        if contains_spam_words(local_part):
            errors.append("Email содержит запрещенные слова.")
        
        return errors 