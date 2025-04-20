import math

# Константы для преобразования
MM_PER_INCH = 25.4
POINTS_PER_INCH = 72.0

def mm_to_pixels(mm: float, dpi: float) -> int:
    """Преобразует миллиметры в пиксели при заданном DPI"""
    inches = mm / MM_PER_INCH
    return int(round(inches * dpi))

def pixels_to_mm(px: float, dpi: float) -> float:
    """Преобразует пиксели в миллиметры при заданном DPI"""
    inches = px / dpi
    return inches * MM_PER_INCH

def points_to_pixels(pt: float, dpi: float) -> int:
    """Преобразует пункты в пиксели при заданном DPI"""
    return int(round((pt / POINTS_PER_INCH) * dpi))

def pixels_to_points(px: float, dpi: float) -> float:
    """Преобразует пиксели в пункты при заданном DPI"""
    return (px / dpi) * POINTS_PER_INCH

def mm_to_points(mm: float) -> float:
    """Преобразует миллиметры в пункты"""
    inches = mm / MM_PER_INCH
    return inches * POINTS_PER_INCH

def points_to_mm(pt: float) -> float:
    """Преобразует пункты в миллиметры"""
    inches = pt / POINTS_PER_INCH
    return inches * MM_PER_INCH

def calculate_dimensions(width: int, height: int, units: str, dpi: int) -> tuple[int, int]:
    """
    Пересчитывает размеры в пиксели в зависимости от единиц измерения
    """
    if units.lower() == "px":
        return width, height
    elif units.lower() == "mm":
        width_px = mm_to_pixels(width, dpi)
        height_px = mm_to_pixels(height, dpi)
        return width_px, height_px
    elif units.lower() == "pt":
        width_px = points_to_pixels(width, dpi)
        height_px = points_to_pixels(height, dpi)
        return width_px, height_px
    else:
        # По умолчанию считаем, что размеры в пикселях
        return width, height 