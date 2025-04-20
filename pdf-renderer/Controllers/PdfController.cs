using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
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

namespace PdfRenderer.Controllers;

[ApiController]
[Route("api/pdf")]
public class PdfController : ControllerBase
{
    private readonly ILogger<PdfController> _logger;

    public PdfController(ILogger<PdfController> logger)
    {
        _logger = logger;
    }

    [HttpPost("render")]
    public IActionResult Render([FromBody] PdfRendererRequest request)
    {
        try
        {
            _logger.LogInformation($"Received PDF rendering request with {request.Pages.Count} pages");

            // Настройка поддержки CMYK
            CssDeclarationValidationMaster.SetValidator(new CssDeviceCmykAwareValidator());

            List<byte[]> pdfPages = new List<byte[]>();

            // Рендеринг каждой страницы отдельно
            for (int i = 0; i < request.Pages.Count; i++)
            {
                var page = request.Pages[i];
                
                // Используем baseUri из запроса
                string baseUri = page.BaseUri ?? "/tmp";
                _logger.LogInformation($"Using baseUri: {baseUri}");
                
                // Преобразование единиц измерения для размера страницы
                float width = 595; // значение по умолчанию A4 в пунктах
                float height = 842; // значение по умолчанию A4 в пунктах
                
                if (page.Width > 0 && page.Height > 0)
                {
                    // Преобразуем в пункты из мм или пикселей
                    width = UnitConverter.ConvertToPoints(page.Width, page.Units);
                    height = UnitConverter.ConvertToPoints(page.Height, page.Units);
                    _logger.LogInformation($"Page {i+1}: Setting explicit page size {width}x{height} pt");
                }
                
                // Создаем настройки конвертера с правильными шрифтами
                var converterProperties = CreateConverterProperties(baseUri);
                
                // Создаем новый поток для страницы PDF
                using var pageStream = new MemoryStream();
                var htmlBytes = Encoding.UTF8.GetBytes(page.Html ?? string.Empty);
                
                _logger.LogInformation($"Page {i+1}: Converting HTML to PDF...");
                
                // Создаем PdfWriter, который НЕ будет закрывать MemoryStream
                using var writer = new PdfWriter(pageStream);
                writer.SetCloseStream(false);
                using var pdfDocument = new PdfDocument(writer);

                // Устанавливаем размер страницы
                pdfDocument.SetDefaultPageSize(new PageSize(width, height));

                // Используем отдельный блок для контроля жизненного цикла htmlStream
                using (var htmlStream = new MemoryStream(htmlBytes))
                {
                    // Конвертируем HTML в документ PDF
                    HtmlConverter.ConvertToDocument(htmlStream, pdfDocument, converterProperties);
                }
                // PdfDocument и PdfWriter будут закрыты здесь, но pageStream останется открытым

                // Сбрасываем позицию и получаем байты
                pageStream.Position = 0;
                var pdfBytes = pageStream.ToArray();
                pdfPages.Add(pdfBytes);
                // pageStream будет закрыт автоматически при выходе из using блока
                
                _logger.LogInformation($"Page {i+1}: Conversion complete, PDF size: {pdfBytes.Length} bytes");
            }

            // Если всего одна страница, возвращаем ее напрямую
            if (pdfPages.Count == 1)
            {
                _logger.LogInformation("Single page PDF, returning directly");
                return File(pdfPages[0], "application/pdf");
            }

            _logger.LogInformation($"Merging {pdfPages.Count} pages into a single PDF");
            
            // Для объединения нескольких страниц используем PdfMerger
            var resultStream = new MemoryStream();
            using (var writer = new PdfWriter(resultStream))
            using (var pdfDocument = new PdfDocument(writer))
            {
                var merger = new PdfMerger(pdfDocument);
                
                foreach (var pdfBytes in pdfPages)
                {
                    using (var pageStream = new MemoryStream(pdfBytes))
                    using (var reader = new PdfReader(pageStream))
                    using (var sourceDoc = new PdfDocument(reader))
                    {
                        merger.Merge(sourceDoc, 1, sourceDoc.GetNumberOfPages());
                    }
                }
            }
            
            // Готовим финальный результат
            resultStream.Position = 0;
            var finalPdf = resultStream.ToArray();
            resultStream.Dispose();
            
            _logger.LogInformation($"PDF rendering completed successfully, size: {finalPdf.Length} bytes");
            return File(finalPdf, "application/pdf");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error rendering PDF");
            return StatusCode(500, new { error = "Failed to render PDF", message = ex.Message });
        }
    }
    
    private ConverterProperties CreateConverterProperties(string baseUri)
    {
        var props = new ConverterProperties();
        
        _logger.LogInformation($"Setting Base URI: {baseUri}");
        props.SetBaseUri(baseUri);
        
        // Создаем наш провайдер шрифтов (базовая реализация без стандартных шрифтов)
        #pragma warning disable 612, 618
        var fontProvider = new DefaultFontProvider(false, false, false);
        #pragma warning restore 612, 618
        
        bool hasAddedFonts = false;
        
        // Проверяем наличие и добавляем шрифты из директории assets
        var assetsDir = System.IO.Path.Combine(baseUri, "assets");
        _logger.LogInformation($"Checking for fonts in: {assetsDir}");
        
        if (Directory.Exists(assetsDir))
        {
            try
            {
                var fontFiles = Directory.GetFiles(assetsDir, "*.ttf")
                    .Concat(Directory.GetFiles(assetsDir, "*.otf"))
                    .ToList();
                
                if (fontFiles.Any())
                {
                    _logger.LogInformation($"Found {fontFiles.Count} font files in {assetsDir}");
                    fontProvider.AddDirectory(assetsDir);
                    hasAddedFonts = true;
                }
                else
                {
                    _logger.LogInformation($"No .ttf or .otf font files found in {assetsDir}");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error accessing fonts in {assetsDir}");
            }
        }
        else
        {
            _logger.LogInformation($"Assets directory not found: {assetsDir}");
        }
        
        // Если не нашли никаких пользовательских шрифтов, включаем стандартные шрифты
        if (!hasAddedFonts)
        {
            _logger.LogInformation("Custom fonts not found or not added. Adding standard PDF fonts.");
            
            // Создаем новый провайдер со стандартными шрифтами
            #pragma warning disable 612, 618
            fontProvider = new DefaultFontProvider(true, false, false);
            #pragma warning restore 612, 618
        }
        
        props.SetFontProvider(fontProvider);
        return props;
    }
    
    // Классы запросов
    public class PdfRendererRequest
    {
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
}