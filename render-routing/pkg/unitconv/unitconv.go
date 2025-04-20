package unitconv

import "math"

const (
	// Константы для преобразования
	MM_PER_INCH     = 25.4
	POINTS_PER_INCH = 72.0
)

// MillimetersToPixels преобразует миллиметры в пиксели при заданном DPI
func MillimetersToPixels(mm float64, dpi float64) int {
	inches := mm / MM_PER_INCH
	return int(math.Round(inches * dpi))
}

// PixelsToMillimeters преобразует пиксели в миллиметры при заданном DPI
func PixelsToMillimeters(px float64, dpi float64) float64 {
	inches := px / dpi
	return inches * MM_PER_INCH
}

// PointsToPixels преобразует пункты в пиксели при заданном DPI
func PointsToPixels(pt float64, dpi float64) int {
	return int(math.Round((pt / POINTS_PER_INCH) * dpi))
}

// PixelsToPoints преобразует пиксели в пункты при заданном DPI
func PixelsToPoints(px float64, dpi float64) float64 {
	return (px / dpi) * POINTS_PER_INCH
}

// MillimetersToPoints преобразует миллиметры в пункты
func MillimetersToPoints(mm float64) float64 {
	inches := mm / MM_PER_INCH
	return inches * POINTS_PER_INCH
}

// PointsToMillimeters преобразует пункты в миллиметры
func PointsToMillimeters(pt float64) float64 {
	inches := pt / POINTS_PER_INCH
	return inches * MM_PER_INCH
}
