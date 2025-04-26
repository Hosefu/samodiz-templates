from jinja2 import Environment, Template, meta, exceptions
from typing import Dict, Any, Optional, List, Set
from loguru import logger
import re


class TemplateEngine:
    """
    Класс для обработки шаблонов с использованием Jinja2.
    Поддерживает старый синтаксис {{variable}} и новый {% if condition %}...{% endif %}
    """
    
    def __init__(self):
        """Инициализация окружения Jinja2 с настройками"""
        # Создаем окружение с конфигурацией
        self.env = Environment(
            variable_start_string='{{',
            variable_end_string='}}',
            block_start_string='{%',
            block_end_string='%}',
            comment_start_string='{#',
            comment_end_string='#}',
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True  # Защита от XSS
        )
        
        logger.info("Template engine initialized")
        
    def render_template(self, template_html: str, data: Dict[str, Any]) -> str:
        """
        Обрабатывает шаблон, подставляя в него данные.
        
        Args:
            template_html: HTML-код шаблона с плейсхолдерами
            data: Словарь с данными для подстановки в шаблон
            
        Returns:
            str: Обработанный HTML-код
        """
        try:
            # Проверяем, использует ли шаблон новый синтаксис с условными блоками
            has_conditional_blocks = '{%' in template_html
            
            if has_conditional_blocks:
                # Если в шаблоне есть условные блоки, используем Jinja2
                logger.debug("Template uses conditional blocks, using Jinja2")
                return self._render_with_jinja(template_html, data)
            else:
                # Если в шаблоне только простые плейсхолдеры, можем использовать совместимый метод
                logger.debug("Template uses simple placeholders, using compatible method")
                return self._render_simple_template(template_html, data)
                
        except Exception as e:
            logger.exception(f"Error rendering template: {str(e)}")
            raise
    
    def _render_with_jinja(self, template_html: str, data: Dict[str, Any]) -> str:
        """
        Рендеринг шаблона с использованием Jinja2.
        Поддерживает все возможности Jinja2, включая условные блоки.
        """
        try:
            # Подготавливаем шаблон
            template = self.env.from_string(template_html)
            
            # Анализируем шаблон для поиска используемых переменных
            ast = self.env.parse(template_html)
            variables = meta.find_undeclared_variables(ast)
            
            # Логируем используемые переменные для отладки
            logger.debug(f"Template requires variables: {variables}")
            
            # Проверка наличия всех необходимых переменных в данных
            missing_vars = [var for var in variables if var not in data]
            if missing_vars:
                logger.warning(f"Missing variables in data: {missing_vars}")
            
            # Рендерим шаблон с данными
            rendered_html = template.render(**data)
            
            # Анализируем результат на наличие неподставленных плейсхолдеров
            # Это может помочь в отладке, но их наличие не является ошибкой,
            # так как они могут быть в условных блоках, которые не выполнились
            self._check_for_unrendered_placeholders(rendered_html)
            
            return rendered_html
            
        except exceptions.TemplateSyntaxError as e:
            logger.error(f"Template syntax error: {str(e)}")
            # Добавляем более подробное сообщение с контекстом
            error_line = e.lineno
            error_context = template_html.split('\n')[max(0, error_line-2):error_line+1]
            error_details = f"Syntax error at line {error_line}: {str(e)}\nContext:\n" + "\n".join(error_context)
            raise ValueError(error_details)
            
        except Exception as e:
            logger.error(f"Error in Jinja2 rendering: {str(e)}")
            raise
    
    def _render_simple_template(self, template_html: str, data: Dict[str, Any]) -> str:
        """
        Простая замена плейсхолдеров {{variable}} на значения.
        Обеспечивает обратную совместимость со старым форматом.
        """
        result = template_html
        
        # Находим все плейсхолдеры в шаблоне
        placeholders = re.findall(r'{{([^{}]+)}}', template_html)
        
        for placeholder in placeholders:
            # Удаляем пробелы с краев имени переменной
            var_name = placeholder.strip()
            
            # Заменяем плейсхолдер на значение или пустую строку, если значение отсутствует
            value = str(data.get(var_name, ''))
            result = result.replace('{{' + placeholder + '}}', value)
            
            # Логируем для отладки
            if var_name not in data:
                logger.warning(f"Variable '{var_name}' not found in data")
        
        return result
    
    def _check_for_unrendered_placeholders(self, html: str) -> None:
        """
        Проверяет наличие неподставленных плейсхолдеров в результирующем HTML.
        Используется для логирования потенциальных проблем.
        """
        # Для простых плейсхолдеров {{var}}
        simple_placeholders = re.findall(r'{{([^{}]+)}}', html)
        
        # Для блочных конструкций {% if ... %}
        block_placeholders = re.findall(r'{%([^{}]+)%}', html)
        
        if simple_placeholders:
            logger.warning(f"Unrendered placeholders found: {simple_placeholders}")
            
        if block_placeholders:
            logger.warning(f"Unrendered block statements found: {block_placeholders}")