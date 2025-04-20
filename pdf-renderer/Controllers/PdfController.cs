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
using System.Text;
using iText.Kernel.Pdf;
using iText.Layout;
using iText.Html2pdf;
using iText.Kernel.Geom;
using PdfRenderer.Utils;
using iText.Kernel.Utils;
using iText.Html2pdf.Resolver.Font;
using iText.StyledXmlParser.Css.Validate.Impl;

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
    public IActionResult Render([FromBody] PdfRendererRequest request)
    {
        try
        {
            _logger.LogInformation($"Received PDF rendering request with {request.Pages.Count} pages");

            List<byte[]> pdfPages = new List<byte[]>();

            for (int i = 0; i < request.Pages.Count; i++)
            {
                var page = request.Pages[i];

                _logger.LogInformation($"Rendering page {i+1}: Width={page.Width}, Height={page.Height}, Units={page.Units}, BaseUri={page.BaseUri}");

                using var pageStream = new MemoryStream();

                var converterProperties = CreateConverterProperties(page.BaseUri);

                if (page.Width.HasValue && page.Height.HasValue)
                {
                    float width = UnitConverter.ConvertToPoints(page.Width.Value, page.Units);
                    float height = UnitConverter.ConvertToPoints(page.Height.Value, page.Units);
                    var pageSize = new PageSize(width, height);
                    _logger.LogInformation($"Page {i+1}: Setting explicit page size {width}x{height} pt");
                }

                _logger.LogInformation($"Page {i+1}: Converting HTML to PDF...");
                using (var htmlStream = new MemoryStream(Encoding.UTF8.GetBytes(page.Html ?? string.Empty)))
                {
                    HtmlConverter.ConvertToPdf(htmlStream, pageStream, converterProperties);
                }
                 _logger.LogInformation($"Page {i+1}: Conversion complete, stream length: {pageStream.Length}");

                pdfPages.Add(pageStream.ToArray());
            }

            if (pdfPages.Count == 1)
            {
                _logger.LogInformation("Returning single page PDF.");
                return File(pdfPages[0], "application/pdf");
            }

            _logger.LogInformation($"Merging {pdfPages.Count} pages...");
            using var resultStream = new MemoryStream();
            using (var resultWriter = new PdfWriter(resultStream))
            {
                resultWriter.SetSmartMode(true);
                using (var resultDoc = new PdfDocument(resultWriter))
                {
                    PdfMerger merger = new PdfMerger(resultDoc);

                    foreach (byte[] pdfBytes in pdfPages)
                    {
                        using (var srcStream = new MemoryStream(pdfBytes))
                        using (var reader = new PdfReader(srcStream))
                        {
                            reader.SetUnethicalReading(true);
                            using (var srcDoc = new PdfDocument(reader))
                            {
                                merger.Merge(srcDoc, 1, srcDoc.GetNumberOfPages());
                            }
                        }
                    }
                }
            }

            byte[] finalPdf = resultStream.ToArray();
            _logger.LogInformation($"Merging complete. Final PDF size: {finalPdf.Length} bytes");

            return File(finalPdf, "application/pdf");
        }
        catch (ValidationException validationEx)
        {
            _logger.LogWarning(validationEx, "Validation error during PDF rendering");
            return BadRequest(new { error = "Validation failed", details = validationEx.Errors.Select(e => e.ErrorMessage) });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error rendering PDF");
            return StatusCode(500, new { error = "Failed to render PDF", message = ex.ToString() });
        }
    }

    private ConverterProperties CreateConverterProperties(string baseUri)
    {
        var props = new ConverterProperties();

        if (!string.IsNullOrWhiteSpace(baseUri)) {
             _logger.LogInformation($"Setting Base URI: {baseUri}");
             props.SetBaseUri(baseUri);
        } else {
            _logger.LogWarning("Base URI is not provided or empty.");
        }

        #pragma warning disable 0612 // DefaultFontProvider is obsolete
        var fontProvider = new DefaultFontProvider(false, false, false);
        #pragma warning restore 0612
        bool hasAddedFonts = false;

        if (!string.IsNullOrWhiteSpace(baseUri))
        {
            var assetsDir = System.IO.Path.Combine(baseUri, "assets");
             _logger.LogInformation($"Checking for fonts in: {assetsDir}");
            if (Directory.Exists(assetsDir))
            {
                try {
                    var fontFiles = Directory.GetFiles(assetsDir, "*.ttf")
                        .Concat(Directory.GetFiles(assetsDir, "*.otf"))
                        .ToList();

                    if (fontFiles.Any())
                    {
                        _logger.LogInformation($"Found {fontFiles.Count} font files in {assetsDir}. Adding directory to FontProvider.");
                        fontProvider.AddDirectory(assetsDir);
                        hasAddedFonts = true;
                    }
                     else {
                        _logger.LogInformation($"No .ttf or .otf font files found in {assetsDir}.");
                    }
                } catch (Exception ex) {
                     _logger.LogError(ex, $"Error accessing or reading font files from {assetsDir}");
                }
            } else {
                 _logger.LogInformation($"Assets directory not found: {assetsDir}");
            }
        } else {
             _logger.LogWarning("Cannot check for fonts in assets directory because Base URI is not set.");
        }

        if (!hasAddedFonts)
        {
            _logger.LogInformation("Custom fonts not found or not added. Adding standard PDF fonts.");
            #pragma warning disable 0612 // DefaultFontProvider is obsolete
            fontProvider = new DefaultFontProvider(true, true, true);
            #pragma warning restore 0612
        }

        props.SetFontProvider(fontProvider);
        return props;
    }

    public class PdfRendererRequest
    {
        public List<PdfPageRequest> Pages { get; set; } = new List<PdfPageRequest>();
        public Dictionary<string, object> Data { get; set; } = new Dictionary<string, object>();
        public bool GeneratePreview { get; set; }
    }

    public class PdfPageRequest
    {
        public required string Html { get; set; }
        public float? Width { get; set; }
        public float? Height { get; set; }
        public string Units { get; set; } = "pt";
        public float? Bleed { get; set; }
        public Dictionary<string, object> Config { get; set; } = new Dictionary<string, object>();
        public required string BaseUri { get; set; }
    }
}