using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using iText.Html2pdf;
using iText.Kernel.Geom;
using iText.Kernel.Pdf;
using iText.Layout;
using iText.Kernel.Utils;
using PdfRenderer.Utils;
using iText.StyledXmlParser.Css.Validate.Impl;
using iText.Html2pdf.Resolver.Font;
using iText.StyledXmlParser.Css.Validate;
using Microsoft.Extensions.Logging;
using PdfRenderer.Services;
using System.Net.Http;
using System.Diagnostics;

namespace PdfRenderer.Controllers;

[ApiController]
[Route("api/pdf")]
public class PdfController : ControllerBase
{
    private readonly ILogger<PdfController> _logger;
    private readonly TemplateCacheService _cacheService;
    private readonly IPdfRenderService _pdfRenderService;

    public PdfController(
        ILogger<PdfController> logger,
        TemplateCacheService cacheService,
        IPdfRenderService pdfRenderService)
    {
        _logger = logger;
        _cacheService = cacheService;
        _pdfRenderService = pdfRenderService;
    }

    [HttpGet("health")]
    public IActionResult HealthCheck()
    {
        return Ok(new { status = "ok", service = "pdf-renderer" });
    }

    [HttpPost("render")]
    public async Task<IActionResult> Render([FromBody] PdfRendererRequest request)
    {
        // Start timing for performance tracking
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            // Log the full request details for debugging
            _logger.LogInformation("--- PDF RENDER REQUEST START ---");
            _logger.LogInformation($"Received PDF rendering request with {request.Pages?.Count ?? 0} pages");
            
            // Validate request
            if (request.Pages == null || request.Pages.Count == 0)
            {
                _logger.LogError("Request contains no pages - rejecting");
                return BadRequest(new { error = "Request must contain at least one page" });
            }

            // Log template ID and page information
            _logger.LogInformation($"Template ID: {request.TemplateId}, Generate Preview: {request.GeneratePreview}");
            
            for (int i = 0; i < request.Pages.Count; i++)
            {
                var page = request.Pages[i];
                _logger.LogInformation($"Page {i+1} Info: Width={page.Width}, Height={page.Height}, Units={page.Units}");
                
                // Log HTML content preview for debugging (first 200 chars)
                string htmlPreview = page.Html?.Substring(0, Math.Min(page.Html?.Length ?? 0, 200)) ?? "NULL";
                _logger.LogInformation($"Page {i+1} HTML Preview: {htmlPreview}...");
                
                // Validate HTML content
                if (string.IsNullOrWhiteSpace(page.Html))
                {
                    _logger.LogError($"Page {i+1} has empty or null HTML content");
                    return BadRequest(new { error = $"Page {i+1} has empty HTML content" });
                }
            }

            // Try to load template if ID is provided
            if (request.TemplateId > 0)
            {
                try
                {
                    _logger.LogInformation($"Loading template {request.TemplateId} from cache");
                    var template = await _cacheService.GetTemplateAsync(request.TemplateId);
                    _logger.LogInformation($"Template loaded: {template.Name}, Version: {template.Version}, Pages: {template.Pages.Count}");
                    
                    // Set baseUri for each page
                    for (int i = 0; i < request.Pages.Count && i < template.Pages.Count; i++)
                    {
                        string pageDir = System.IO.Path.Combine(_cacheService.CacheRoot, request.TemplateId.ToString(), template.Pages[i].Name);
                        request.Pages[i].BaseUri = pageDir;
                        _logger.LogInformation($"Set baseUri for page {i+1}: {pageDir}");
                        
                        // Verify the directory exists
                        if (!Directory.Exists(pageDir))
                        {
                            _logger.LogWarning($"BaseUri directory does not exist: {pageDir}");
                        }
                        else
                        {
                            // Check for assets directory
                            string assetsDir = System.IO.Path.Combine(pageDir, "assets");
                            if (Directory.Exists(assetsDir))
                            {
                                var files = Directory.GetFiles(assetsDir);
                                _logger.LogInformation($"Assets directory contains {files.Length} files");
                                foreach (var file in files.Take(5)) // Log first 5 files
                                {
                                    _logger.LogInformation($"Asset file: {System.IO.Path.GetFileName(file)}");
                                }
                            }
                            else
                            {
                                _logger.LogWarning($"Assets directory does not exist: {assetsDir}");
                            }
                        }
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error loading template, continuing with default settings");
                }
            }

            // Prepare for PDF generation
            _logger.LogInformation("Configuring CSS validator for CMYK support");
            CssDeclarationValidationMaster.SetValidator(new CssDeviceCmykAwareValidator());

            List<byte[]> pdfPages = new List<byte[]>();
            
            // Render each page
            for (int i = 0; i < request.Pages.Count; i++)
            {
                var page = request.Pages[i];
                _logger.LogInformation($"--- RENDERING PAGE {i+1} OF {request.Pages.Count} ---");
                
                // Get baseUri
                string baseUri = page.BaseUri ?? "/tmp";
                _logger.LogInformation($"Using baseUri: {baseUri}");
                
                // Handle assets if needed
                if (baseUri.Contains("storage-service") && page.Settings != null && page.Settings.ContainsKey("assets"))
                {
                    _logger.LogInformation("Processing asset information from settings");
                    string assetsStr = page.Settings["assets"];
                    try 
                    {
                        // Parse assets list
                        var options = new JsonSerializerOptions
                        {
                            PropertyNameCaseInsensitive = true
                        };
                        
                        var assets = JsonSerializer.Deserialize<List<AssetInfo>>(assetsStr, options);
                        if (assets != null && assets.Count > 0)
                        {
                            _logger.LogInformation($"Found {assets.Count} assets to download");
                            
                            // Create a temporary directory for assets
                            string tempAssetsDir = System.IO.Path.Combine(System.IO.Path.GetTempPath(), Guid.NewGuid().ToString());
                            Directory.CreateDirectory(tempAssetsDir);
                            Directory.CreateDirectory(System.IO.Path.Combine(tempAssetsDir, "assets"));
                            _logger.LogInformation($"Created temp assets directory: {tempAssetsDir}");
                            
                            // Download each asset
                            using var httpClient = new HttpClient();
                            int downloadedCount = 0;
                            
                            foreach (var asset in assets)
                            {
                                try 
                                {
                                    string assetPath = asset.File;
                                    if (!string.IsNullOrEmpty(assetPath) && !assetPath.StartsWith("/"))
                                    {
                                        assetPath = "/" + assetPath;
                                    }
                                    
                                    string assetUrl = $"{baseUri}{assetPath}";
                                    _logger.LogInformation($"Downloading asset: {assetUrl}, Asset.File={asset.File}");
                                    
                                    var assetData = await httpClient.GetByteArrayAsync(assetUrl);
                                    string fileName = System.IO.Path.GetFileName(asset.File);
                                    string savePath = System.IO.Path.Combine(tempAssetsDir, "assets", fileName);
                                    
                                    System.IO.File.WriteAllBytes(savePath, assetData);
                                    _logger.LogInformation($"Asset saved to {savePath}, size: {assetData.Length} bytes");
                                    downloadedCount++;
                                }
                                catch (Exception assetEx)
                                {
                                    _logger.LogError(assetEx, $"Error downloading asset {asset.File}");
                                }
                            }
                            
                            _logger.LogInformation($"Downloaded {downloadedCount} of {assets.Count} assets");
                            
                            // Update baseUri to use local assets
                            baseUri = tempAssetsDir;
                            _logger.LogInformation($"Updated baseUri to use local assets: {baseUri}");
                        }
                    }
                    catch (Exception ex)
                    {
                        _logger.LogError(ex, "Error processing assets from settings");
                    }
                }
                
                // Convert dimensions
                float width = 595; // default A4 in points
                float height = 842; // default A4 in points
                
                if (page.Width > 0 && page.Height > 0)
                {
                    // Convert to points from mm or pixels
                    width = UnitConverter.ConvertToPoints(page.Width, page.Units);
                    height = UnitConverter.ConvertToPoints(page.Height, page.Units);
                    _logger.LogInformation($"Page dimensions: {page.Width}x{page.Height} {page.Units} -> {width}x{height} pt");
                }
                
                // Create converter properties with appropriate font handling
                var converterProperties = CreateConverterProperties(baseUri);
                
                // FIX: Use a different approach for HTML to PDF conversion that handles streams better
                try
                {
                    _logger.LogInformation($"Converting HTML to PDF, content length: {page.Html?.Length ?? 0} characters");
                    
                    // Create HTML stream outside the MemoryStream to ensure proper content
                    byte[] htmlBytes = Encoding.UTF8.GetBytes(page.Html ?? string.Empty);
                    _logger.LogInformation($"HTML content converted to {htmlBytes.Length} bytes");
                    
                    // Use PdfRenderService for more reliable conversion
                    string[] baseUris = new string[] { baseUri };
                    string[] htmlContents = new string[] { page.Html ?? string.Empty };
                    
                    // Simplified approach for single page
                    using (var ms = new MemoryStream())
                    {
                        _logger.LogInformation("Starting HTML to PDF conversion");
                        
                        // First approach - direct conversion to MemoryStream
                        try
                        {
                            using (var htmlStream = new MemoryStream(htmlBytes))
                            {
                                // Ensure the stream is at the beginning
                                htmlStream.Position = 0;
                                
                                // Create PageSize object to set dimensions
                                PageSize pageSize = new PageSize(width, height);
                                
                                // Add page size to properties using the correct method
                                converterProperties.SetBaseUri(baseUri);
                                
                                // Create a PDF writer with the specified page size
                                PdfWriter pdfWriter = new PdfWriter(ms);
                                PdfDocument pdfDocument = new PdfDocument(pdfWriter);
                                pdfDocument.SetDefaultPageSize(pageSize);
                                
                                // Now convert the HTML to PDF
                                HtmlConverter.ConvertToPdf(htmlStream, pdfDocument, converterProperties);
                                
                                _logger.LogInformation("HTML converted to PDF successfully");
                            }
                            
                            // Get the PDF bytes
                            byte[] pdfBytes = ms.ToArray();
                            _logger.LogInformation($"PDF size: {pdfBytes.Length} bytes");
                            pdfPages.Add(pdfBytes);
                        }
                        catch (Exception ex)
                        {
                            _logger.LogError(ex, "Error converting HTML to PDF, trying alternate approach");
                            
                            // Fall back to render service
                            var pdfData = _pdfRenderService.RenderPdf(
                                htmlContents.ToList(),
                                baseUris.ToList(),
                                page.Settings ?? new Dictionary<string, string>()
                            );
                            
                            if (pdfData != null && pdfData.Length > 0)
                            {
                                _logger.LogInformation($"Fallback successful, PDF size: {pdfData.Length} bytes");
                                pdfPages.Add(pdfData);
                            }
                            else
                            {
                                _logger.LogError("Fallback PDF generation failed - empty result");
                                return BadRequest(new { error = "Failed to convert HTML to PDF with both methods" });
                            }
                        }
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error in PDF generation");
                    return StatusCode(500, new { error = "Internal server error during PDF generation", details = ex.Message });
                }
            }
            
            _logger.LogInformation($"Successfully rendered {pdfPages.Count} PDF pages");
            
            // Check if we need to merge multiple pages
            byte[] finalPdf;
            
            if (pdfPages.Count == 1)
            {
                _logger.LogInformation("Single page PDF, no merging needed");
                finalPdf = pdfPages[0];
            }
            else
            {
                _logger.LogInformation($"Merging {pdfPages.Count} PDF pages into single document");
                try
                {
                    using (var outputStream = new MemoryStream())
                    {
                        using (var pdfWriter = new PdfWriter(outputStream))
                        {
                            using (var pdfDocument = new PdfDocument(pdfWriter))
                            {
                                PdfMerger merger = new PdfMerger(pdfDocument);
                                
                                foreach (var pdfPage in pdfPages)
                                {
                                    using (var sourceStream = new MemoryStream(pdfPage))
                                    {
                                        using (var sourcePdf = new PdfDocument(new PdfReader(sourceStream)))
                                        {
                                            merger.Merge(sourcePdf, 1, sourcePdf.GetNumberOfPages());
                                        }
                                    }
                                }
                            }
                        }
                        
                        finalPdf = outputStream.ToArray();
                    }
                    
                    _logger.LogInformation($"PDF merge successful, final size: {finalPdf.Length} bytes");
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error merging PDFs");
                    return StatusCode(500, new { error = "Internal server error during PDF merging", details = ex.Message });
                }
            }
            
            // Generate file name
            string pdfFileName = request.TemplateId > 0 
                ? $"template-{request.TemplateId}-{DateTime.Now:yyyyMMddHHmmss}.pdf" 
                : $"document-{DateTime.Now:yyyyMMddHHmmss}.pdf";
            
            // Save a copy of the generated PDF if needed for debugging or caching
            if (request.GeneratePreview)
            {
                try
                {
                    string previewsDirectory = System.IO.Path.Combine(Directory.GetCurrentDirectory(), "wwwroot");
                    Directory.CreateDirectory(previewsDirectory);
                    string previewPath = System.IO.Path.Combine(previewsDirectory, pdfFileName);
                    _logger.LogInformation($"Saving preview copy to {previewPath}");
                    System.IO.File.WriteAllBytes(previewPath, finalPdf);
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error saving preview copy");
                    // Do not fail the entire process because of this
                }
            }
            
            // Log performance information
            stopwatch.Stop();
            _logger.LogInformation($"Total PDF generation time: {stopwatch.ElapsedMilliseconds}ms");
            _logger.LogInformation($"Final PDF size: {finalPdf.Length} bytes");
            _logger.LogInformation("--- PDF RENDER REQUEST END ---");
            
            // Return the PDF file
            return File(finalPdf, "application/pdf", pdfFileName);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unhandled exception in PDF rendering");
            return StatusCode(500, new { error = "Internal server error", details = ex.Message });
        }
    }

    // Create converter properties with appropriate font handling
    private ConverterProperties CreateConverterProperties(string baseUri)
    {
        var converterProperties = new ConverterProperties();
        
        // Set base URI for relative resources
        converterProperties.SetBaseUri(baseUri);
        
        // Configure default font provider
        var defaultFontProvider = new DefaultFontProvider();
        defaultFontProvider.AddDirectory("/app/wwwroot/fonts");
        
        // Add standard fonts
        defaultFontProvider.AddStandardPdfFonts();
        
        // Check for fonts in assets directory
        string assetsDir = System.IO.Path.Combine(baseUri, "assets");
        if (Directory.Exists(assetsDir))
        {
            _logger.LogInformation($"Adding assets directory to font provider: {assetsDir}");
            defaultFontProvider.AddDirectory(assetsDir);
            
            // Log available font files
            var fontFiles = Directory.GetFiles(assetsDir, "*.ttf").Concat(Directory.GetFiles(assetsDir, "*.otf")).ToList();
            foreach (var font in fontFiles)
            {
                _logger.LogInformation($"Found font file: {System.IO.Path.GetFileName(font)}");
            }
        }
        else
        {
            _logger.LogWarning($"Assets directory not found: {assetsDir}");
        }
        
        // Add system fonts if running on Linux
        if (System.Runtime.InteropServices.RuntimeInformation.IsOSPlatform(System.Runtime.InteropServices.OSPlatform.Linux))
        {
            string[] linuxFontDirs = {
                "/usr/share/fonts",
                "/usr/local/share/fonts",
                "/usr/share/fonts/truetype"
            };
            
            foreach (var fontDir in linuxFontDirs)
            {
                if (Directory.Exists(fontDir))
                {
                    _logger.LogInformation($"Adding Linux font directory: {fontDir}");
                    defaultFontProvider.AddDirectory(fontDir);
                }
            }
        }
        
        // Configure the font provider
        converterProperties.SetFontProvider(defaultFontProvider);
        
        // Return the configured properties
        return converterProperties;
    }

    // Request model classes
    public class PdfRendererRequest
    {
        public int TemplateId { get; set; }
        public List<PdfPageRequest> Pages { get; set; } = new List<PdfPageRequest>();
        public Dictionary<string, string> Data { get; set; } = new Dictionary<string, string>();
        public bool GeneratePreview { get; set; }
    }
    
    public class PdfPageRequest
    {
        public string Html { get; set; } = string.Empty;
        public int Width { get; set; }
        public int Height { get; set; }
        public string Units { get; set; } = "mm";
        public int Bleeds { get; set; }
        public Dictionary<string, string> Settings { get; set; } = new Dictionary<string, string>();
        public string BaseUri { get; set; } = string.Empty;
    }
    
    public class AssetInfo
    {
        [JsonPropertyName("file")]
        public string File { get; set; } = string.Empty;
    }
}