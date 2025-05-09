"""
Клиент для взаимодействия с микросервисами рендеринга.

Обеспечивает унифицированный интерфейс для различных типов рендеринга (PDF, PNG, SVG).
"""
import io
import json
import logging
import requests
from typing import Tuple, Dict, Any, BinaryIO, Union, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class RendererError(Exception):
    """Исключение, возникающее при ошибках рендеринга."""
    pass


class RendererClient:
    """
    Клиент для взаимодействия с микросервисами рендеринга.
    
    Поддерживает различные форматы: PDF, PNG, SVG.
    """
    
    def __init__(self, format_type: str, renderer_url: Optional[str] = None, format_obj: Optional['Format'] = None):
        """
        Инициализирует клиент для указанного формата.
        
        Args:
            format_type: Тип формата ('pdf', 'png', 'svg')
            renderer_url: (optional) URL рендерера
            format_obj: (optional) Объект Format из БД
        """
        self.format_type = format_type.lower()
        
        # Если передан объект Format, используем его URL
        if format_obj:
            self.renderer_url = format_obj.render_url
        # Если URL передан явно, используем его
        elif renderer_url:
            self.renderer_url = renderer_url
        else:
            # Если ничего не передано, пытаемся найти формат в БД
            from apps.templates.models import Format
            try:
                fmt = Format.objects.get(name=format_type)
                self.renderer_url = fmt.render_url
            except Format.DoesNotExist:
                raise ValueError(f"Format '{format_type}' not found in database")
        
        # Устанавливаем content_type
        if self.format_type == 'pdf':
            self.content_type = 'application/pdf'
        elif self.format_type == 'png':
            self.content_type = 'image/png'
        elif self.format_type == 'svg':
            self.content_type = 'image/svg+xml'
        
        logger.debug(f"Initialized {self.format_type} renderer client with URL: {self.renderer_url}")
    
    def render(self, html: str, options: Dict[str, Any]) -> Tuple[BinaryIO, str]:
        """
        Выполняет рендеринг HTML в указанный формат.
        
        Args:
            html: HTML-код для рендеринга
            options: Опции рендеринга (специфичные для формата)
        
        Returns:
            Tuple[BinaryIO, str]: (байты документа, content_type)
        
        Raises:
            RendererError: В случае ошибки рендеринга
        """
        try:
            # Подготавливаем запрос
            payload = {
                'html': html,
                'options': options
            }
            
            # Выполняем запрос к микросервису
            response = requests.post(
                self.renderer_url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': self.content_type
                },
                timeout=180  # Соответствует таймауту Celery
            )
            
            # Проверяем успешность запроса
            response.raise_for_status()
            
            # Проверяем MIME-тип ответа
            if not response.headers.get('Content-Type', '').startswith(self.content_type):
                raise RendererError(
                    f"Unexpected content type received: {response.headers.get('Content-Type')}"
                )
            
            # Возвращаем байты документа и content-type
            return io.BytesIO(response.content), response.headers.get('Content-Type')
        
        except requests.exceptions.ConnectionError as e:
            # Улучшаем сообщение об ошибке подключения
            logger.error(f"Unable to connect to renderer at {self.renderer_url}: {e}")
            raise RendererError(
                f"Сервис рендеринга {self.format_type} недоступен. "
                f"Проверьте, что микросервис {self.renderer_url} запущен и доступен."
            ) from e
        
        except requests.RequestException as e:
            # Обрабатываем ошибки сетевых запросов
            logger.error(f"Request error while rendering {self.format_type}: {e}")
            error_message = str(e)
            
            # Если есть ответ от сервера, пытаемся извлечь детали ошибки
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    if 'error' in error_data:
                        error_message = error_data['error']
                    elif 'message' in error_data:
                        error_message = error_data['message']
                except (ValueError, json.JSONDecodeError):
                    # Если не удается разобрать JSON, используем текст ответа
                    if e.response.text:
                        error_message = e.response.text[:200]  # Ограничиваем длину сообщения
            
            raise RendererError(f"Failed to render {self.format_type}: {error_message}") from e
        
        except Exception as e:
            # Обрабатываем прочие ошибки
            logger.error(f"Unexpected error while rendering {self.format_type}: {e}")
            raise RendererError(f"Unexpected error in {self.format_type} rendering: {str(e)}") from e