namespace PdfRenderer.Models;

/// <summary>
/// Результат рендеринга PDF
/// </summary>
public class RenderResult
{
    /// <summary>
    /// URL превью (PNG), если было запрошено
    /// </summary>
    public string PreviewUrl { get; set; } = string.Empty;
    
    /// <summary>
    /// Сообщение об ошибке (если есть)
    /// </summary>
    public string Error { get; set; } = string.Empty;
}