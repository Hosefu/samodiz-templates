from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class TemplateRenderRequest(BaseModel):
    """
    Модель запроса для рендеринга шаблона
    """
    # HTML-содержимое шаблона с плейсхолдерами
    template_html: str = Field(..., description="HTML template with placeholders")
    
    # Данные для подстановки в шаблон
    data: Optional[Dict[str, Any]] = Field(default=None, description="Data to be injected into the template")
    
    # ID шаблона (для логирования)
    template_id: Optional[int] = Field(default=None, description="Template ID for tracking")
    
    # Индекс страницы (для многостраничных шаблонов)
    page_index: Optional[int] = Field(default=0, description="Page index for multi-page templates")