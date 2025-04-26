from pydantic import BaseModel, Field
from typing import Optional


class TemplateRenderResponse(BaseModel):
    """
    Модель ответа на запрос рендеринга шаблона
    """
    # Обработанный HTML
    html: str = Field(..., description="Rendered HTML content")
    
    # Статус обработки
    status: str = Field(default="success", description="Processing status")
    
    # Сообщение об ошибке (если есть)
    error: Optional[str] = Field(default=None, description="Error message if processing failed")


class HealthResponse(BaseModel):
    """
    Модель ответа на запрос проверки здоровья
    """
    status: str = Field(default="ok", description="Service status")
    service: str = Field(default="template-service", description="Service name")