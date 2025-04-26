from fastapi import APIRouter, HTTPException, Depends, Response
from loguru import logger
from typing import Optional, Dict, Any

from app.models.request import TemplateRenderRequest
from app.models.response import TemplateRenderResponse, HealthResponse
from app.services.template_engine import TemplateEngine

router = APIRouter()
template_engine = TemplateEngine()

@router.post("/render", response_model=TemplateRenderResponse)
async def render_template(request: TemplateRenderRequest):
    """
    Обрабатывает HTML-шаблон, подставляя данные в плейсхолдеры.
    Поддерживает условные конструкции и другие возможности Jinja2.
    """
    logger.info(f"Received template render request: template_id={request.template_id}, page_index={request.page_index}")
    
    try:
        # Проверяем, что шаблон передан
        if not request.template_html:
            logger.error("Empty template_html provided")
            raise HTTPException(status_code=400, detail="Template HTML is required")
        
        # Используем шаблонизатор для обработки HTML
        logger.debug(f"Processing template, length: {len(request.template_html)} chars")
        processed_html = template_engine.render_template(
            template_html=request.template_html,
            data=request.data or {}
        )
        
        # Формируем ответ
        logger.info("Template rendered successfully")
        return TemplateRenderResponse(
            html=processed_html,
            status="success"
        )
        
    except Exception as e:
        logger.exception(f"Error rendering template: {str(e)}")
        
        # Если ошибка связана с шаблонизацией, возвращаем 400
        if "jinja2" in str(e).lower() or "template" in str(e).lower():
            raise HTTPException(status_code=400, detail=f"Template processing error: {str(e)}")
        
        # Иначе возвращаем общую ошибку сервера
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Проверка работоспособности сервиса
    """
    return HealthResponse(status="ok", service="template-service")