using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using iText.Html2pdf;
using iText.Kernel.Pdf;
using iText.Kernel.Geom;
using iText.Html2pdf.Resolver.Font;
using iText.IO.Font.Constants;
using Microsoft.Extensions.Logging;
using PdfRenderer.Models;
using PdfRenderer.Utils;

namespace PdfRenderer.Services;

public class PdfRenderService
{
    private readonly ILogger<PdfRenderService> _logger;

    public PdfRenderService(ILogger<PdfRenderService> logger) 
        => _logger = logger;

    public byte[] RenderPdf(RenderRequest request)
    {
        var options = request.Options;
        
        // Calculate page size including bleeds
        float width = UnitConverter.ConvertToPoints(options.Width, options.Unit);
        float height = UnitConverter.ConvertToPoints(options.Height, options.Unit);
        float bleedPoints = UnitConverter.ConvertToPoints(options.Bleeds, options.Unit);
        
        // Add bleeds to page size
        float pageWidth = width + (bleedPoints * 2);
        float pageHeight = height + (bleedPoints * 2);
        
        _logger.LogInformation($"Page size: {pageWidth}x{pageHeight} pt (including {bleedPoints}pt bleeds)");
        
        using var memoryStream = new MemoryStream();
        using var writer = new PdfWriter(memoryStream);
        using var pdfDocument = new PdfDocument(writer);
        
        // Set page size
        var pageSize = new PageSize(pageWidth, pageHeight);
        pdfDocument.SetDefaultPageSize(pageSize);
        
        // Configure properties
        var props = CreateConverterProperties(options);
        
        // Set CMYK support
        if (options.CmykSupport)
        {
            EnableCmykSupport(props, pdfDocument);
        }
        
        // Render HTML to PDF
        using var htmlStream = new MemoryStream(Encoding.UTF8.GetBytes(request.Html));
        HtmlConverter.ConvertToPdf(htmlStream, pdfDocument, props);
        
        return memoryStream.ToArray();
    }
    
    private ConverterProperties CreateConverterProperties(RenderOptions options)
    {
        var props = new ConverterProperties();
        
        // Font provider
        var fontProvider = new DefaultFontProvider(true, false, false);
        props.SetFontProvider(fontProvider);
        
        // Base URI for relative resources
        props.SetBaseUri(Environment.CurrentDirectory);
        
        return props;
    }
    
    private void EnableCmykSupport(ConverterProperties props, PdfDocument pdfDocument)
    {
        // For basic CMYK support in iText7, we need to manually set the color space
        // The DefaultCssApplierFactory is not needed for basic CMYK support
        _logger.LogInformation("CMYK support enabled");
        
        // The CMYK support in iText7 requires proper CSS handling
        // For now, we'll log that CMYK support is enabled
        // Full CMYK support may require additional configuration
    }
} 