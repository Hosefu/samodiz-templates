import os
import uuid
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from loguru import logger
from playwright.async_api import async_playwright
from PIL import Image

from app.config import settings
from app.models.request import RenderRequest
from app.utils.unit_converter import calculate_dimensions

# Создаем семафор для ограничения количества параллельных браузеров
browser_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_BROWSERS)

class PngRenderer:
    """
    Сервис для рендеринга HTML в PNG-изображения с использованием Playwright
    """
    
    def __init__(self):
        """Инициализация сервиса рендеринга"""
        self.temp_dir = settings.TEMP_DIR
        self.output_dir = settings.OUTPUT_DIR
        self.default_dpi = settings.DEFAULT_DPI
        self.timeout = settings.TIMEOUT
        self.browser_type = settings.BROWSER_TYPE
        self.browser_headless = settings.BROWSER_HEADLESS
        self.browser_args = settings.BROWSER_ARGS

    async def render_png(self, request: RenderRequest) -> Tuple[bytes, Optional[str]]:
        """
        Рендерит HTML в PNG-изображение с ограничением параллельных запросов
        
        Args:
            request: Данные запроса на рендеринг
            
        Returns:
            Tuple[bytes, Optional[str]]: Бинарные данные изображения и сообщение об ошибке (если есть)
        """
        try:
            # Получаем DPI из настроек или используем значение по умолчанию
            dpi = int(request.get_setting('dpi', self.default_dpi))
            
            # Прозрачность фона
            transparent = request.get_setting('transparency', 'false').lower() == 'true'
            
            # Расчет размера в пикселях
            width, height = self._calculate_dimensions(request.width, request.height, request.units, dpi)
            
            # Генерируем уникальное имя для файла
            file_id = str(uuid.uuid4())
            html_path = os.path.join(self.temp_dir, f"{file_id}.html")
            output_path = os.path.join(self.output_dir, f"{file_id}.png")
            
            # Для больших HTML используем запись по частям
            html_size = len(request.html)
            if html_size > settings.MAX_HTML_SIZE:  # если больше максимального размера
                logger.warning(f"Large HTML detected: {html_size/1_000_000:.2f}MB (max: {settings.MAX_HTML_SIZE/1_000_000:.2f}MB)")
                with open(html_path, 'w', encoding='utf-8') as f:
                    # Записываем по частям, чтобы не держать всё в памяти
                    chunk_size = 100_000
                    for i in range(0, html_size, chunk_size):
                        f.write(request.html[i:i+chunk_size])
            else:
                # Для обычных HTML просто записываем
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(request.html)
            
            logger.info(f"Rendering HTML to PNG with dimensions: {width}x{height}px, DPI: {dpi}")
            
            # Используем семафор для ограничения количества параллельных браузеров
            async with browser_semaphore:
                try:
                    # Запускаем Playwright и рендерим HTML в PNG с таймаутом
                    image_bytes = await asyncio.wait_for(
                        self._render_with_playwright(
                            html_path=html_path,
                            width=width,
                            height=height,
                            output_path=output_path,
                            transparent=transparent
                        ),
                        timeout=settings.RENDER_TIMEOUT
                    )
                except asyncio.TimeoutError:
                    return bytes(), f"Rendering timeout after {settings.RENDER_TIMEOUT} seconds"
            
            # Удаляем временный HTML-файл
            os.remove(html_path)
            
            return image_bytes, None
            
        except Exception as e:
            logger.error(f"Error rendering PNG: {str(e)}")
            return bytes(), f"Error rendering PNG: {str(e)}"

    async def _render_with_playwright(self, html_path: str, width: int, height: int, 
                                    output_path: str, transparent: bool) -> bytes:
        """
        Рендерит HTML в PNG с использованием Playwright с обработкой таймаутов
        """
        try:
            async with asyncio.timeout(settings.RENDER_TIMEOUT):
                async with async_playwright() as p:
                    # Выбираем тип браузера
                    if self.browser_type == "firefox":
                        browser_type = p.firefox
                    elif self.browser_type == "webkit":
                        browser_type = p.webkit
                    else:
                        browser_type = p.chromium
                        
                    # Запускаем браузер
                    browser = await browser_type.launch(
                        headless=self.browser_headless, 
                        args=self.browser_args
                    )
                    
                    # Создаем новый контекст
                    context = await browser.new_context(
                        viewport={'width': width, 'height': height}
                    )
                    
                    # Открываем новую страницу
                    page = await context.new_page()
                    
                    # Если нужен прозрачный фон
                    if transparent:
                        await page.add_style_tag(content="""
                            html, body {
                                background-color: transparent !important;
                            }
                        """)
                        
                    # Загружаем HTML из файла с обработкой таймаута
                    try:
                        await page.goto(
                            f"file://{html_path}", 
                            wait_until="networkidle", 
                            timeout=self.timeout * 1000
                        )
                    except Exception as e:
                        logger.error(f"Error loading page: {str(e)}")
                        # Даже если таймаут, пробуем сделать скриншот того, что успело загрузиться
                        logger.warning("Trying to capture partial render after timeout")
                    
                    # Настройки снимка экрана
                    screenshot_options = {
                        'path': output_path,
                        'full_page': True,
                        'type': 'png',
                        'omit_background': transparent
                    }
                    
                    # Делаем снимок экрана
                    await page.screenshot(**screenshot_options)
                    
                    # Закрываем браузер
                    await browser.close()
                    
                    # Читаем сгенерированный файл
                    with open(output_path, 'rb') as f:
                        image_bytes = f.read()
                        
                    # Удаляем файл
                    os.remove(output_path)
                    
                    return image_bytes
                    
        except asyncio.TimeoutError:
            logger.error(f"Rendering timed out after {settings.RENDER_TIMEOUT} seconds")
            raise RuntimeError(f"Rendering timeout exceeded ({settings.RENDER_TIMEOUT}s)")

    def _calculate_dimensions(self, width: int, height: int, units: str, dpi: int) -> Tuple[int, int]:
        """
        Пересчитывает размеры в пиксели в зависимости от единиц измерения
        """
        return calculate_dimensions(width, height, units, dpi)


# Создаем экземпляр рендерера для использования в приложении
png_renderer = PngRenderer()