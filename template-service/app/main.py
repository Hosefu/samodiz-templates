import os
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger

from app.api.routes import router as api_router
from app.utils.logger import setup_logging

# Настройка логирования
setup_logging()

# Настройки приложения
APP_NAME = os.getenv("TEMPLATE_SERVICE_NAME", "template-service")
HOST = os.getenv("TEMPLATE_SERVICE_HOST", "0.0.0.0")
PORT = int(os.getenv("TEMPLATE_SERVICE_PORT", "8083"))
DEBUG = os.getenv("TEMPLATE_SERVICE_DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("TEMPLATE_SERVICE_LOG_LEVEL", "INFO").upper()

# Создание экземпляра приложения
app = FastAPI(
    title=APP_NAME,
    description="Сервис шаблонизации для системы генерации документов",
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
app.include_router(api_router, prefix="/api/template")

# Обработчик исключений
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Обработчик событий запуска
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {APP_NAME}")
    logger.info(f"Server running at http://{HOST}:{PORT}")
    logger.info(f"Documentation available at http://{HOST}:{PORT}/api/docs")

# Обработчик событий завершения
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {APP_NAME}")

# Запуск приложения (при прямом выполнении файла)
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level=LOG_LEVEL.lower()
    )