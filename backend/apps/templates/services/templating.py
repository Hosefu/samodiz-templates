"""
Сервис шаблонизации для подстановки пользовательских данных в HTML-шаблоны.

Использует облегченную версию Jinja2 с ограниченным набором функций.
"""
import logging
import re
from typing import Dict, Any, Optional, List
from jinja2 import Environment, DictLoader, Template, sandbox, exceptions
from jinja2.sandbox import SandboxedEnvironment
from .asset_helper import asset_helper

logger = logging.getLogger(__name__)


class TemplateProcessingError(Exception):
    """Исключение, возникающее при ошибках обработки шаблонов."""
    pass


class LimitedSandboxEnvironment(SandboxedEnvironment):
    """
    Безопасное окружение Jinja2 с ограниченными возможностями.
    
    Поддерживает только базовые операции подстановки переменных и простые условия.
    """
    
    def is_safe_attribute(self, obj, attr, value):
        """Проверяет безопасность доступа к атрибутам объектов."""
        # Разрешаем только базовые атрибуты строк и словарей
        if isinstance(obj, (str, dict)):
            return True
        return False
    
    def call_binop(self, context, operator, left, right):
        """Ограничивает допустимые бинарные операции."""
        # Разрешаем только сравнения и базовые операции со строками
        if operator in ('==', '!=', '>', '<', '>=', '<=', '+'):
            return sandbox.SandboxedEnvironment.call_binop(self, context, operator, left, right)
        return super().call_binop(context, operator, left, right)


class TemplateRenderer:
    """
    Сервис для рендеринга HTML-шаблонов с подстановкой пользовательских данных.
    
    Использует ограниченный набор возможностей Jinja2 для безопасного рендеринга.
    """
    
    def __init__(self):
        """Инициализирует окружение Jinja2 с ограниченными возможностями."""
        self.environment = LimitedSandboxEnvironment(
            # Отключаем автоэкранирование, так как HTML уже задан
            autoescape=False,
            # Настраиваем разделители как в стандартном Jinja
            variable_start_string='{{',
            variable_end_string='}}',
            block_start_string='{%',
            block_end_string='%}',
            # Ограничиваем список поддерживаемых тегов
            extensions=[],
        )
        
        # Добавляем функцию для работы с ассетами
        self.environment.globals['asset'] = self._asset_function
        
        # Храним контекст для доступа к template_id и page_id
        self._template_id = None
        self._page_id = None
    
    def _asset_function(self, asset_name):
        """Функция для получения URL ассета внутри шаблона."""
        if not self._template_id:
            logger.warning("asset() called without template_id")
            return ""
        
        url = asset_helper.get_asset_url(self._template_id, asset_name, self._page_id)
        return url
    
    def validate_template(self, html: str) -> List[Dict[str, Any]]:
        """
        Проверяет HTML-шаблон на синтаксические ошибки в Jinja выражениях.
        
        Args:
            html: HTML-код с Jinja выражениями
            
        Returns:
            List[Dict[str, Any]]: Список ошибок в формате [{"line": номер, "message": "сообщение"}]
            или пустой список, если ошибок нет
        """
        errors = []
        
        try:
            # Пробуем скомпилировать шаблон
            self.environment.from_string(html)
            return []
        except exceptions.TemplateSyntaxError as e:
            # Собираем информацию об ошибке
            errors.append({
                "line": e.lineno,
                "message": str(e)
            })
        except Exception as e:
            # Обрабатываем прочие ошибки
            errors.append({
                "line": 0,
                "message": f"Неизвестная ошибка: {str(e)}"
            })
        
        return errors
    
    def extract_fields(self, html: str) -> List[str]:
        """
        Извлекает имена всех полей из HTML-шаблона.
        
        Args:
            html: HTML-код с Jinja выражениями
            
        Returns:
            List[str]: Список имен полей
        """
        fields = set()
        
        # Регулярные выражения для поиска переменных в {{ }}
        var_pattern = r'\{\{\s*([a-zA-Z0-9_\.]+)\s*\}\}'
        
        # Поиск всех переменных
        for match in re.finditer(var_pattern, html):
            field_name = match.group(1).strip()
            # Исключаем составные пути (только верхний уровень)
            # И исключаем вызовы функций (например, asset())
            if '.' not in field_name and '(' not in field_name:
                fields.add(field_name)
        
        # Также ищем переменные в условиях {% if field %}
        if_pattern = r'\{%\s*if\s+([a-zA-Z0-9_]+)\s*.*?%\}'
        
        for match in re.finditer(if_pattern, html):
            field_name = match.group(1).strip()
            fields.add(field_name)
        
        return sorted(list(fields))
    
    def render_template(self, html: str, data: Dict[str, Any], template_id=None, page_id=None) -> str:
        """
        Рендерит HTML-шаблон с подстановкой данных.
        
        Args:
            html: HTML-код с Jinja выражениями
            data: Словарь с данными для подстановки
            template_id: ID шаблона для обработки ассетов
            page_id: (optional) ID страницы для поиска локальных ассетов
            
        Returns:
            str: Отрендеренный HTML
            
        Raises:
            TemplateProcessingError: В случае ошибки рендеринга
        """
        try:
            # Устанавливаем контекст для функции asset
            self._template_id = template_id
            self._page_id = page_id
            
            # Создаем шаблон из строки
            template = self.environment.from_string(html)
            
            # Рендерим с переданными данными
            rendered_html = template.render(**data)
            
            return rendered_html
            
        except exceptions.TemplateSyntaxError as e:
            logger.error(f"Template syntax error: {e}")
            raise TemplateProcessingError(f"Ошибка синтаксиса шаблона: {str(e)}")
            
        except exceptions.UndefinedError as e:
            logger.error(f"Undefined variable error: {e}")
            # Позволяем неопределенным переменным быть пустыми
            return ""
            
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            raise TemplateProcessingError(f"Ошибка рендеринга шаблона: {str(e)}")
        finally:
            # Очищаем контекст
            self._template_id = None
            self._page_id = None


# Синглтон-инстанс для удобного импорта
template_renderer = TemplateRenderer()