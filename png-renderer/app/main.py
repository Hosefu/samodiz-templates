import os
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger

from app.config import settings
from app.api.routes import router as api_router


# Настройка логирования
logger.remove()
logger.add(
    sys.stdout,
    format="{time} | {level} | {message}",
    level=settings.LOG_LEVEL,
    colorize=True
)
logger.add(
    "logs/png-renderer.log",
    rotation="10 MB",
    retention="3 days",
    level=settings.LOG_LEVEL
)


# Создание экземпляра приложения
app = FastAPI(
    title=settings.APP_NAME,
    description="Сервис рендеринга HTML в PNG-изображения",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)


# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Регистрация маршрутов API
app.include_router(api_router, prefix="/api/png")


# Обработчик исключений
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# Обработчик событий запуска
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME}")
    
    # Создаем необходимые директории
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs(settings.CACHE_DIR, exist_ok=True)
    
    logger.info(f"Server running at http://{settings.HOST}:{settings.PORT}")
    logger.info(f"Documentation available at http://{settings.HOST}:{settings.PORT}/api/docs")


# Обработчик событий завершения
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.APP_NAME}")


# Запуск приложения (при прямом выполнении файла)
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )