from pydantic import BaseModel
from typing import Optional


class RenderResponse(BaseModel):
    """
    Модель ответа на запрос рендеринга
    """
    # Сообщение об ошибке (если есть)
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """
    Модель ответа на запрос проверки здоровья
    """
    status: str = "ok"
    service: str = "png-renderer"