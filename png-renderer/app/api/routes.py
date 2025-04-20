from fastapi import APIRouter, HTTPException, Response, Depends
from loguru import logger
from typing import Optional

from app.models.request import RenderRequest
from app.models.response import RenderResponse, HealthResponse
from app.services.renderer import png_renderer
from app.services.cache import template_cache

router = APIRouter()


@router.post("/render", response_model=None)
async def render_png(request: RenderRequest):
    """
    Рендерит HTML в PNG-изображение
    """
    logger.info(f"Received render request: {request.width}x{request.height} {request.units}")
    
    try:
        # Проверяем кэш
        cache_key = template_cache.get_cache_key(
            html=request.html,
            width=request.width,
            height=request.height,
            units=request.units,
            settings_dict=request.settings
        )
        
        cached_image = template_cache.get_from_cache(cache_key)
        if cached_image:
            logger.info("Returning cached image")
            return Response(content=cached_image, media_type="image/png")
        
        # Рендерим изображение
        image_bytes, error = await png_renderer.render_png(request)
        
        # Проверяем наличие ошибки
        if error:
            logger.error(f"Error rendering PNG: {error}")
            return RenderResponse(error=error)
        
        # Сохраняем в кэш
        template_cache.save_to_cache(
            cache_key=cache_key,
            image_data=image_bytes,
            metadata={
                "width": request.width,
                "height": request.height,
                "units": request.units
            }
        )
        
        # Возвращаем изображение
        return Response(content=image_bytes, media_type="image/png")
        
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Проверка работоспособности сервиса
    """
    return HealthResponse()