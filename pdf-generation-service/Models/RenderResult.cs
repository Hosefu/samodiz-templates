namespace PdfGenerator.Models;

public class RenderResult
{
    public string PdfPath { get; set; } = string.Empty;
    public string PreviewPath { get; set; } = string.Empty;
    public string Error { get; set; } = string.Empty;
}