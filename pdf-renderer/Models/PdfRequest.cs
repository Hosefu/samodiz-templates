using System.Collections.Generic;

namespace PdfRenderer.Models;

/// <summary>
/// Запрос на рендеринг PDF
/// </summary>
public class PdfRequest
{
    /// <summary>
    /// HTML-содержимое для рендеринга
    /// </summary>
    public required string Html { get; set; }
    
    /// <summary>
    /// Ширина страницы
    /// </summary>
    public float Width { get; set; }
    
    /// <summary>
    /// Высота страницы
    /// </summary>
    public float Height { get; set; }
    
    /// <summary>
    /// Единицы измерения (px, mm)
    /// </summary>
    public string Units { get; set; } = "mm";
    
    /// <summary>
    /// Подрезы для печати (bleed)
    /// </summary>
    public int Bleeds { get; set; }
    
    /// <summary>
    /// Генерировать ли PNG-превью
    /// </summary>
    public bool GeneratePreview { get; set; }
    
    /// <summary>
    /// Дополнительные настройки рендеринга
    /// </summary>
    public Dictionary<string, string>? Settings { get; set; }
}