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
        Рендерит HTML в PNG-изображение
        
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
            
            # Записываем HTML во временный файл
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(request.html)
            
            logger.info(f"Rendering HTML to PNG with dimensions: {width}x{height}px, DPI: {dpi}")
            
            # Запускаем Playwright и рендерим HTML в PNG
            image_bytes = await self._render_with_playwright(
                html_path=html_path,
                width=width,
                height=height,
                output_path=output_path,
                transparent=transparent
            )
            
            # Удаляем временный HTML-файл
            os.remove(html_path)
            
            return image_bytes, None
            
        except Exception as e:
            logger.error(f"Error rendering PNG: {str(e)}")
            return bytes(), f"Error rendering PNG: {str(e)}"

    async def _render_with_playwright(self, html_path: str, width: int, height: int, 
                                     output_path: str, transparent: bool) -> bytes:
        """
        Рендерит HTML в PNG с использованием Playwright
        
        Args:
            html_path: Путь к HTML-файлу
            width: Ширина в пикселях
            height: Высота в пикселях
            output_path: Путь для сохранения результата
            transparent: Использовать прозрачный фон
            
        Returns:
            bytes: Бинарные данные изображения
        """
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
                
            # Загружаем HTML из файла
            await page.goto(f"file://{html_path}", wait_until="networkidle", timeout=self.timeout * 1000)
            
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

    def _calculate_dimensions(self, width: int, height: int, units: str, dpi: int) -> Tuple[int, int]:
        """
        Пересчитывает размеры в пиксели в зависимости от единиц измерения
        
        Args:
            width: Ширина
            height: Высота
            units: Единицы измерения (px, mm)
            dpi: Разрешение в точках на дюйм
            
        Returns:
            Tuple[int, int]: Ширина и высота в пикселях
        """
        if units.lower() == "px":
            return width, height
        elif units.lower() == "mm":
            # Переводим миллиметры в дюймы, затем в пиксели
            # 1 мм = 0.03937 дюйма
            width_px = int(round((width * 0.03937) * dpi))
            height_px = int(round((height * 0.03937) * dpi))
            return width_px, height_px
        else:
            # По умолчанию считаем, что размеры в пикселях
            return width, height


# Создаем экземпляр рендерера для использования в приложении
png_renderer = PngRenderer()