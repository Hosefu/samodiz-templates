using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Collections.Generic;
using iText.Html2pdf;
using iText.Kernel.Pdf;
using iText.Kernel.Geom;
using iText.Layout.Font;
using iText.IO.Font.Constants;
using iText.StyledXmlParser.Css.Validate;
using iText.StyledXmlParser.Css.Validate.Impl;
using iText.Kernel.Utils;
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
        float width = UnitConverter.ConvertToPoints(options.Width, options.Unit, options.Dpi);
        float height = UnitConverter.ConvertToPoints(options.Height, options.Unit, options.Dpi);
        float bleedPoints = UnitConverter.ConvertToPoints(options.Bleeds, options.Unit, options.Dpi);
        
        // Add bleeds to page size
        float pageWidth = width + (bleedPoints * 2);
        float pageHeight = height + (bleedPoints * 2);
        
        _logger.LogInformation($"Page size: {pageWidth}x{pageHeight} pt (including {bleedPoints}pt bleeds)");
        
        using var memoryStream = new MemoryStream();
        var writerProps = new WriterProperties();
        using var writer = new PdfWriter(memoryStream, writerProps);
        using var pdfDocument = new PdfDocument(writer);
        pdfDocument.SetCloseWriter(false);
        
        // Set page size
        var pageSize = new PageSize(pageWidth, pageHeight);
        pdfDocument.SetDefaultPageSize(pageSize);
        
        // Configure properties
        var props = CreateConverterProperties(options);
        
        // Set CMYK support
        if (options.CmykSupport)
        {
            EnableCmykSupport(props, pdfDocument, options.ColorProfilePath);
        }
        
        // Render HTML to PDF
        using var htmlStream = new MemoryStream(Encoding.UTF8.GetBytes(request.Html));
        var document = HtmlConverter.ConvertToDocument(htmlStream, pdfDocument, props);

        if (pdfDocument.GetNumberOfPages() != 1)
        {
            document.Close();
            throw new InvalidOperationException($"Expected 1 page, got {pdfDocument.GetNumberOfPages()}");
        }

        document.Close();
        // Stream remains open due to WriterProperties
        return memoryStream.ToArray();
    }
    
    private ConverterProperties CreateConverterProperties(RenderOptions options)
    {
        var props = new ConverterProperties();

        string baseUri = options.BaseUri ?? Environment.CurrentDirectory;

        // Font provider and assets directory
        var fontProvider = new FontProvider();
        fontProvider.AddStandardPdfFonts();
        fontProvider.AddSystemFonts();

        var assetsDir = System.IO.Path.Combine(baseUri, "assets");
        if (Directory.Exists(assetsDir))
        {
            fontProvider.AddDirectory(assetsDir);
        }

        props.SetFontProvider(fontProvider);

        // Base URI for relative resources
        props.SetBaseUri(baseUri);
        
        return props;
    }
    
    private void EnableCmykSupport(ConverterProperties props, PdfDocument pdfDocument, string? profilePath)
    {
        _logger.LogInformation("CMYK support enabled");
        // Allow device-cmyk() colors in CSS
        CssDeclarationValidationMaster.SetValidator(new CssDeviceCmykAwareValidator());

        if (!string.IsNullOrEmpty(profilePath) && File.Exists(profilePath))
        {
            _logger.LogInformation($"Using ICC profile: {profilePath}");
            using var profileStream = File.OpenRead(profilePath);
            var outputIntent = new PdfOutputIntent("Custom", "", "", "CMYK", profileStream);
            props.SetDocumentOutputIntent(outputIntent);
        }
    }

    public byte[] CombinePdfs(IEnumerable<byte[]> pdfFiles)
    {
        using var ms = new MemoryStream();
        using var writer = new PdfWriter(ms);
        using var pdfDoc = new PdfDocument(writer);
        var merger = new PdfMerger(pdfDoc);

        foreach (var bytes in pdfFiles)
        {
            using var src = new PdfDocument(new PdfReader(new MemoryStream(bytes)));
            merger.Merge(src, 1, src.GetNumberOfPages());
        }

        merger.Close();
        return ms.ToArray();
    }
}
