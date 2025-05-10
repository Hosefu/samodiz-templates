namespace PdfRenderer.Models;

public class RenderRequest
{
    public required string Html { get; set; }
    public required RenderOptions Options { get; set; }
}

public class RenderOptions
{
    public required string Format { get; set; } = "pdf";
    public required float Width { get; set; }
    public required float Height { get; set; }
    public required string Unit { get; set; }
    public int Dpi { get; set; } = 300;
    public bool CmykSupport { get; set; } = true;
    public float Bleeds { get; set; } = 0;
} 