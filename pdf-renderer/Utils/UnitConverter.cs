using System;

namespace PdfRenderer.Utils
{
    public static class UnitConverter
    {
        // Константы для преобразования
        private const float MM_PER_INCH = 25.4f;
        private const float POINTS_PER_INCH = 72.0f;

        /// <summary>
        /// Распознает единицы измерения и преобразует в пункты (для PDF)
        /// </summary>
        public static float ConvertToPoints(float value, string units, float dpi = 96)
        {
            return units.ToLower() switch
            {
                "mm" => MillimetersToPoints(value),
                "pt" => value,
                "px" => PixelsToPoints(value, dpi),
                _ => value,
            };
        }
        
        /// <summary>
        /// Преобразует миллиметры в пункты (используется в PDF)
        /// </summary>
        public static float MillimetersToPoints(float mm)
        {
            float inches = mm / MM_PER_INCH;
            return inches * POINTS_PER_INCH;
        }
        
        /// <summary>
        /// Преобразует пиксели в пункты при заданном DPI
        /// </summary>
        public static float PixelsToPoints(float px, float dpi)
        {
            return (px / dpi) * POINTS_PER_INCH;
        }
    }
}