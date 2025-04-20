// Controllers/PdfController.cs
using Microsoft.AspNetCore.Mvc;
using FluentValidation;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using PdfRenderer.Models;
using PdfRenderer.Services;
using Microsoft.Extensions.Logging;
using System.IO;
using iText.Kernel.Pdf;
using iText.Layout;
using iText.Html2pdf;
using iText.Kernel.Geom;
using PdfRenderer.Utils;

namespace PdfRenderer.Controllers;

[ApiController]
[Route("api/[controller]")]
public class PdfController : ControllerBase
{
    private readonly IValidator<PdfRequest> _validation;
    private readonly ILogger<PdfController> _logger;
    private readonly IPdfRenderService _render;
    private readonly IPreviewService _preview;

    public PdfController(
        IValidator<PdfRequest> validation,
        ILogger<PdfController> logger,
        IPdfRenderService render,
        IPreviewService preview)
    {
        _validation = validation;
        _logger = logger;
        _render = render;
        _preview = preview;
    }

    [HttpPost("render")]
    public async Task<IActionResult> Render([FromBody] PdfRendererRequest request)
    {
        try
        {
            _logger.LogInformation($"Received PDF rendering request with {request.Pages.Count} pages");

            using var memoryStream = new MemoryStream();
            using var pdfWriter = new PdfWriter(memoryStream);
            using var pdf = new PdfDocument(pdfWriter);
            using var document = new Document(pdf);

            foreach (var page in request.Pages)
            {
                // Convert dimensions to points if needed
                float width = UnitConverter.ConvertToPoints(page.Width.GetValueOrDefault(595), page.Units);
                float height = UnitConverter.ConvertToPoints(page.Height.GetValueOrDefault(842), page.Units);

                var pageSize = new PageSize(width, height);

                // Create a new page with specified dimensions
                var pdfPage = pdf.AddNewPage(pageSize);
                document.SetPage(pdfPage);

                // Convert HTML to PDF
                var converterProperties = new ConverterProperties();
                HtmlConverter.ConvertToPdf(page.Html, pdf, converterProperties);

                // Apply bleed if specified
                if (page.Bleed.HasValue && page.Bleed.Value > 0)
                {
                    var bleed = UnitConverter.ConvertToPoints(page.Bleed.Value, page.Units);
                    pdfPage.SetCropBox(new Rectangle(
                        -bleed,
                        -bleed,
                        pageSize.GetWidth() + (2 * bleed),
                        pageSize.GetHeight() + (2 * bleed)
                    ));
                }
            }

            document.Close();

            var fileBytes = memoryStream.ToArray();
            _logger.LogInformation($"Generated PDF with {request.Pages.Count} pages, size: {fileBytes.Length} bytes");

            return File(fileBytes, "application/pdf");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error rendering PDF");
            return StatusCode(500, new { error = "Failed to render PDF", message = ex.Message });
        }
    }

    [HttpGet("health")]
    public IActionResult Health()
    {
        return Ok(new { status = "healthy" });
    }
}

public class PdfRendererRequest
{
    public List<PdfPageRequest> Pages { get; set; } = new List<PdfPageRequest>();
    public Dictionary<string, object> Data { get; set; } = new Dictionary<string, object>();
    public bool GeneratePreview { get; set; }
}

public class PdfPageRequest
{
    public string Html { get; set; }
    public float? Width { get; set; }
    public float? Height { get; set; }
    public string Units { get; set; } = "pt";
    public float? Bleed { get; set; }
    public Dictionary<string, object> Config { get; set; } = new Dictionary<string, object>();
}